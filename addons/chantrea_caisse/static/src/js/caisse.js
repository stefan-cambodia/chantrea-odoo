// Caisse en dollars qui accepte les riels : total et reste en riels, espèces « $ + ៛ »,
// monnaie rendue en dollars entiers + riels, KHQR en riels, ticket et clôture.
import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { Dialog } from "@web/core/dialog/dialog";
import { formatCurrency, getCurrency } from "@web/core/currency";
import { formatFloat } from "@web/core/utils/numbers";
import { ConnectionLostError } from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { PaymentScreenStatus } from "@point_of_sale/app/screens/payment_screen/payment_status/payment_status";
import { QRPopup } from "@point_of_sale/app/components/popups/qr_code_popup/qr_code_popup";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { ClosePosPopup } from "@point_of_sale/app/components/popups/closing_popup/closing_popup";
import { ask, makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { aPayerEnRiels, montantRecu, renduMonnaie } from "@chantrea_caisse/js/riels";
import {
    chiffresKhmers,
    dateHeureAnglaise,
    dateHeureKhmere,
    dateKhmere,
    ligneKhmere,
    montantAnglais,
    nombreAnglais,
} from "@chantrea_caisse/js/khmer";

/** Riels avec séparateur de milliers et symbole ៛, selon la langue de l'utilisateur. */
export function formatRiels(montant, khr) {
    if (khr && getCurrency(khr.id)) {
        return formatCurrency(montant, khr.id);
    }
    return `${formatFloat(montant, { digits: [0, 0] })} ៛`;
}

/** Riels à payer pour un montant en dollars (négatif pour un remboursement). */
function enRiels(usd, taux, pas) {
    const signe = usd < 0 ? -1 : 1;
    return signe * aPayerEnRiels(Math.abs(usd), taux, pas);
}

// ---------------------------------------------------------------------------
// Magasin : taux, riel, arrondi ; QR code en riels.
// ---------------------------------------------------------------------------
patch(PosStore.prototype, {
    get chantreaKhr() {
        return this.models["res.currency"].find((c) => c.name === "KHR");
    },
    get chantreaTaux() {
        return this.config.chantrea_taux_caisse || 0;
    },
    get chantreaArrondi() {
        return this.config.chantrea_arrondi_khr || 100;
    },
    chantreaFormatRiels(montant) {
        return formatRiels(montant, this.chantreaKhr);
    },
    chantreaFormatTaux(taux = this.chantreaTaux) {
        return formatFloat(taux, { digits: [0, Number.isInteger(taux) ? 0 : 2] });
    },

    async showQR(payment) {
        const methode = payment.payment_method_id;
        if (methode.payment_method_type !== "qr_code" || methode.qr_code_method !== "emv_qr") {
            return super.showQR(...arguments);
        }
        // KHQR : la référence est le numéro du ticket (le nom de la commande vaut « / » tant
        // qu'elle n'est pas enregistrée). En riels : montant converti au taux de la caisse,
        // arrondi au billet supérieur, et pas de QR code de secours sans montant (il serait en dollars).
        const order = payment.pos_order_id;
        const enRiels = methode.chantrea_khqr_riels;
        const khr = this.chantreaKhr;
        const taux = order.chantreaTaux;
        if (enRiels && (!khr || !taux)) {
            this.dialog.add(AlertDialog, {
                title: _t("Failure to generate Payment QR Code"),
                body: _t("No riel rate is available for the till: the QR code cannot ask for riels."),
            });
            return false;
        }
        const montant = enRiels ? aPayerEnRiels(payment.amount, taux, this.chantreaArrondi) : payment.amount;
        const reference = order.pos_reference || order.tracking_number || "";
        const deviseId = enRiels ? khr.id : this.currency.id;
        let qr;
        payment.chantreaKhqr = null;
        try {
            // QR code et empreinte MD5 de son texte, pour retrouver le paiement chez Bakong.
            const khqr = await this.data.call("pos.payment.method", "chantrea_qr_khqr", [
                [methode.id],
                montant,
                reference,
                deviseId,
                order.partner_id?.id || false,
            ]);
            qr = khqr.qr;
            payment.chantreaKhqr = { ...khqr, montant, deviseId };
        } catch (error) {
            qr = !enRiels && methode.default_qr;
            if (!qr) {
                this.dialog.add(AlertDialog, {
                    title: _t("Failure to generate Payment QR Code"),
                    body:
                        error instanceof ConnectionLostError
                            ? _t("Connection to the server has been lost. Please check your internet connection.")
                            : error.data?.message || String(error),
                });
                return false;
            }
        }
        payment.chantrea_montant_khr = enRiels ? montant : 0;
        payment.qrPaymentData = {
            name: methode.name,
            amount: enRiels ? this.chantreaFormatRiels(montant) : this.env.utils.formatCurrency(montant),
            qrCode: qr,
        };
        return await ask(
            this.env.services.dialog,
            { title: methode.name, line: payment, order, qrCode: qr },
            {},
            QRPopup
        ).then((result) => {
            payment.qrPaymentData = null;
            payment.chantreaKhqr = null;
            return result;
        });
    },
});

// Intervalle entre deux questions à Bakong, plus long après une erreur (ms).
const KHQR_INTERVALLE = 3000;
const KHQR_INTERVALLE_ERREUR = 10000;

patch(QRPopup.prototype, {
    setup() {
        super.setup(...arguments);
        const line = this.props.line;
        if (line.payment_method_id.chantrea_khqr_riels && line.chantrea_montant_khr) {
            const riels = this.env.services.pos.chantreaFormatRiels(line.chantrea_montant_khr);
            this.amount = `${riels} (${this.env.utils.formatCurrency(line.amount)})`;
        }
        // Avec un jeton Bakong, la fenêtre demande régulièrement si le QR code a été payé
        // et confirme d'elle-même ; la caissière peut toujours confirmer ou annuler.
        const khqr = line.chantreaKhqr;
        this.chantreaVerif = useState({ etat: khqr?.verification ? "attente" : "", message: "" });
        if (!khqr?.verification) {
            return;
        }
        const pos = this.env.services.pos;
        let minuterie = null;
        let ouverte = true;
        const verifier = async () => {
            let resultat;
            try {
                resultat = await pos.data.call("pos.payment.method", "chantrea_verifier_khqr", [
                    [line.payment_method_id.id],
                    khqr.md5,
                    khqr.montant,
                    khqr.deviseId,
                ]);
            } catch {
                resultat = {
                    etat: "erreur",
                    message: _t("No connection to the server: check the payment in the banking app."),
                };
            }
            if (!ouverte) {
                return;
            }
            Object.assign(this.chantreaVerif, { message: "", ...resultat });
            if (resultat.etat === "paye") {
                line.transaction_id = resultat.hash;
                this._confirm();
            } else if (resultat.etat === "attente" || resultat.etat === "erreur") {
                minuterie = setTimeout(
                    verifier,
                    resultat.etat === "erreur" ? KHQR_INTERVALLE_ERREUR : KHQR_INTERVALLE
                );
            }
        };
        onMounted(() => {
            minuterie = setTimeout(verifier, KHQR_INTERVALLE);
        });
        onWillUnmount(() => {
            ouverte = false;
            clearTimeout(minuterie);
        });
    },
});

// ---------------------------------------------------------------------------
// Commande : totaux en riels, monnaie rendue, valeurs envoyées au serveur.
// ---------------------------------------------------------------------------
patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        if (!this.chantrea_mode_rendu) {
            this.chantrea_mode_rendu = "mixte";
        }
    },
    get chantreaTaux() {
        return this.chantrea_taux || this.config.chantrea_taux_caisse || 0;
    },
    get chantreaArrondi() {
        return this.config.chantrea_arrondi_khr || 100;
    },
    get chantreaTotalKhr() {
        return enRiels(this.totalDue, this.chantreaTaux, this.chantreaArrondi);
    },
    get chantreaResteKhr() {
        return enRiels(this.remainingDue, this.chantreaTaux, this.chantreaArrondi);
    },
    /** Monnaie à rendre, en dollars et positive (Odoo 19 la compte en négatif). Rien sur un remboursement. */
    get chantreaMonnaieUsd() {
        return this.totalDue >= 0 ? Math.max(-this.change, 0) : 0;
    },
    get chantreaRendu() {
        return renduMonnaie(this.chantreaMonnaieUsd, this.chantreaTaux, this.chantreaArrondi, this.chantrea_mode_rendu);
    },
    setOrderPrices() {
        super.setOrderPrices(...arguments);
        this.chantrea_taux = this.chantreaTaux;
        const rendu = this.chantreaRendu;
        this.chantrea_rendu_usd = rendu.usd;
        this.chantrea_rendu_khr = rendu.khr;
        for (const ligne of this.payment_ids) {
            if (ligne.payment_method_id.is_cash_count && !ligne.is_change && !ligne.chantrea_montant_khr) {
                ligne.chantrea_especes_usd = ligne.getAmount();
            }
        }
    },
});

// ---------------------------------------------------------------------------
// Fenêtre « Espèces $ + ៛ » : billets en dollars et en riels remis par le client.
// ---------------------------------------------------------------------------
export class ChantreaEspecesPopup extends Component {
    static template = "chantrea_caisse.EspecesPopup";
    static components = { Dialog };
    static props = {
        du: Number,
        usd: { type: Number, optional: true },
        khr: { type: Number, optional: true },
        getPayload: Function,
        close: Function,
    };
    static BILLETS_USD = [1, 5, 10, 20, 50, 100];
    static BILLETS_KHR = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000];

    setup() {
        this.pos = usePos();
        this.state = useState({
            usd: this.props.usd ? String(this.props.usd) : "",
            khr: this.props.khr ? String(this.props.khr) : "",
        });
    }
    get billetsUsd() {
        return ChantreaEspecesPopup.BILLETS_USD;
    }
    get billetsKhr() {
        return ChantreaEspecesPopup.BILLETS_KHR;
    }
    get taux() {
        return this.pos.chantreaTaux;
    }
    get usd() {
        const v = parseFloat(String(this.state.usd).replace(",", "."));
        return isNaN(v) || v < 0 ? 0 : Math.round(v * 100) / 100;
    }
    get khr() {
        const v = parseInt(String(this.state.khr).replace(/[\s,.]/g, ""), 10);
        return isNaN(v) || v < 0 ? 0 : v;
    }
    get recu() {
        return montantRecu(this.usd, this.khr, this.taux);
    }
    get duKhr() {
        return aPayerEnRiels(this.props.du, this.taux, this.pos.chantreaArrondi);
    }
    get resteUsd() {
        return Math.max(Math.round((this.props.du - this.recu) * 100) / 100, 0);
    }
    get resteKhr() {
        return aPayerEnRiels(this.resteUsd, this.taux, this.pos.chantreaArrondi);
    }
    get rendu() {
        return renduMonnaie(this.recu - this.props.du, this.taux, this.pos.chantreaArrondi);
    }
    formatUsd(montant) {
        return this.env.utils.formatCurrency(montant);
    }
    formatKhr(montant) {
        return this.pos.chantreaFormatRiels(montant);
    }
    ajouterUsd(billet) {
        this.state.usd = String(Math.round((this.usd + billet) * 100) / 100);
    }
    ajouterKhr(billet) {
        this.state.khr = String(this.khr + billet);
    }
    effacer() {
        this.state.usd = "";
        this.state.khr = "";
    }
    confirmer() {
        this.props.getPayload({ usd: this.usd, khr: this.khr });
        this.props.close();
    }
}

patch(PaymentScreen.prototype, {
    get chantreaMethodeEspeces() {
        return this.payment_methods_from_config.find((pm) => pm.is_cash_count);
    },
    async chantreaSaisirEspeces() {
        const methode = this.chantreaMethodeEspeces;
        if (!methode || !this.pos.chantreaTaux) {
            return;
        }
        const order = this.currentOrder;
        let ligne = this.paymentLines.find((l) => l.payment_method_id.is_cash_count && !l.is_change);
        const nouvelle = !ligne;
        if (nouvelle) {
            if (!(await this.addNewPaymentLine(methode))) {
                return;
            }
            ligne = this.paymentLines.at(-1);
        }
        // Reste dû sans compter cette ligne d'espèces.
        const du = order.currency.round(order.totalDue - (order.amountPaid - ligne.getAmount()));
        const saisie = await makeAwaitable(this.dialog, ChantreaEspecesPopup, {
            du,
            usd: ligne.chantrea_montant_khr ? ligne.chantrea_especes_usd : 0,
            khr: ligne.chantrea_montant_khr || 0,
        });
        if (!saisie) {
            if (nouvelle) {
                this.deletePaymentLine(ligne.uuid);
            }
            return;
        }
        order.selectPaymentline(ligne);
        ligne.setAmount(montantRecu(saisie.usd, saisie.khr, this.pos.chantreaTaux));
        ligne.chantrea_especes_usd = saisie.usd;
        ligne.chantrea_montant_khr = saisie.khr;
        this.numberBuffer.reset();
    },
    updateSelectedPaymentline(amount = false) {
        super.updateSelectedPaymentline(...arguments);
        // Montant tapé au pavé numérique : des dollars seulement.
        const ligne = this.selectedPaymentLine;
        if (ligne && ligne.payment_method_id.is_cash_count && !ligne.is_change) {
            ligne.chantrea_montant_khr = 0;
            ligne.chantrea_especes_usd = ligne.getAmount();
        }
    },
});

patch(PaymentScreenStatus.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },
    chantreaChoisirRendu(mode) {
        this.order.chantrea_mode_rendu = mode;
    },
});

// ---------------------------------------------------------------------------
// Ticket
// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// Ticket du client en khmer et en anglais, quelle que soit la langue de la caissière :
// libellés « ខ្មែរ / English » (gabarits), données en anglais, montants écrits à
// l'anglaise, date en khmer puis jj/mm/aaaa, comme les documents imprimés.
// ---------------------------------------------------------------------------

/** Moment luxon (heure de la caisse) → {jour, mois, annee, heure, minute}. */
function momentDe(date) {
    return date && { jour: date.day, mois: date.month, annee: date.year, heure: date.hour, minute: date.minute };
}

/** Nom anglais d'un enregistrement chargé dans la caisse (à défaut, son nom). */
function nomAnglais(enregistrement) {
    return enregistrement?.chantrea_nom_en || enregistrement?.name || "";
}

/** Nom anglais du produit d'une ligne ; les attributs ajoutés au nom sont gardés tels quels. */
function nomProduitAnglais(ligne) {
    const nom = ligne.full_product_name || "";
    const produit = ligne.product_id;
    const anglais = produit?.product_tmpl_id?.chantrea_nom_en;
    if (anglais && produit.name && nom.startsWith(produit.name)) {
        return anglais + nom.slice(produit.name.length);
    }
    return nom;
}

patch(OrderReceipt.prototype, {
    formatCurrency(amount) {
        return montantAnglais(amount, this.order.currency);
    },
    chantreaFormatRiels(montant) {
        return montantAnglais(montant, { symbol: "៛", position: "after", decimal_places: 0 });
    },
    chantreaFormatTaux() {
        const taux = this.order.chantreaTaux;
        return nombreAnglais(taux, Number.isInteger(taux) ? 0 : 2);
    },
    /** Adresse de la boutique sur une ligne, sans virgule en trop quand la rue est vide. */
    chantreaAdresse() {
        const societe = this.order.company;
        return [societe.street, societe.city, societe.state_id?.code, societe.zip].filter(Boolean).join(", ");
    },
    chantreaMonnaie() {
        return Math.abs(this.order.change);
    },
    chantreaKm(texte) {
        return chiffresKhmers(texte);
    },
    chantreaNom(enregistrement) {
        return nomAnglais(enregistrement);
    },
    chantreaGroupeTaxe(groupe) {
        const enregistrement = this.order.models["account.tax.group"].get(groupe.id);
        return enregistrement?.chantrea_nom_en || groupe.group_name;
    },
    chantreaDateLivraison() {
        const moment = momentDe(this.order.shipping_date);
        return moment ? { km: dateKhmere(moment), en: dateHeureAnglaise(moment).slice(0, 10) } : null;
    },
});

patch(ReceiptHeader.prototype, {
    get chantreaDate() {
        const moment = momentDe(this.order.date_order);
        return moment && { km: dateHeureKhmere(moment), en: dateHeureAnglaise(moment) };
    },
});

patch(Orderline.prototype, {
    get lineScreenValues() {
        const valeurs = super.lineScreenValues;
        const line = this.line;
        if (this.props.mode !== "receipt" || !line.order_id) {
            return valeurs;
        }
        const devise = line.currency;
        const uniteAnglaise = nomAnglais(line.product_id?.uom_id);
        let prix = valeurs.price;
        if (prix) {
            prix = line.getDiscount() === 100 ? "ឥតគិតថ្លៃ / Free" : montantAnglais(line.displayPrice, devise);
        }
        return {
            ...valeurs,
            name: nomProduitAnglais(line),
            price: prix,
            decimalPart: line.getQuantityStr().decimalPart && `.${line.getQuantityStr().decimalPart}`,
            displayPriceUnit:
                valeurs.displayPriceUnit && `${montantAnglais(line.displayPriceUnit, devise)} / ${uniteAnglaise}`,
            noDiscountPrice: montantAnglais(line.displayPriceNoDiscount, devise),
            chantreaKm: prix && ligneKhmere(line.qty, line.displayPrice, devise),
        };
    },
});

// ---------------------------------------------------------------------------
// Clôture : riels attendus dans le tiroir, comptage des dollars et des riels.
// ---------------------------------------------------------------------------
patch(ClosePosPopup.prototype, {
    setup() {
        super.setup(...arguments);
        this.chantreaComptage = useState({ usd: "", khr: "" });
    },
    get chantreaRiels() {
        return this.props.default_cash_details?.chantrea_riels;
    },
    chantreaFormatRiels(montant) {
        return this.pos.chantreaFormatRiels(montant);
    },
    chantreaCompter() {
        const riels = this.chantreaRiels;
        const usd = parseFloat(String(this.chantreaComptage.usd).replace(",", ".")) || 0;
        const khr = parseInt(String(this.chantreaComptage.khr).replace(/[\s,.]/g, ""), 10) || 0;
        const taux = riels?.taux || this.pos.chantreaTaux;
        const valeur = Math.round((usd + (taux ? khr / taux : 0)) * 100) / 100;
        const id = this.props.default_cash_details.id;
        this.state.payments[id].counted = this.env.utils.formatCurrency(valeur, false);
        this.setManualCashInput(this.state.payments[id].counted);
    },
});
