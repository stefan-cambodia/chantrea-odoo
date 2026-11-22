# Textes khmers à relire par un locuteur natif

Fichier généré par `python3 scripts/relecture_km.py`. Ne pas modifier à la main :
corriger le texte khmer à l'endroit indiqué au début de chaque partie, puis
noter le texte comme relu dans `docs/relecture-km-statut.json`
(ex. `{ "km": { "វិក្កយបត្រអាករ": "ok" } }`) et relancer le script.

Tous les textes ci-dessous ont été traduits par Claude depuis l'anglais.
Sur les devis et factures, le khmer est imprimé au-dessus et l'anglais juste en dessous.
Les noms de pays ne sont pas listés : ils viennent du référentiel Unicode CLDR
(`addons/chantrea_portail/i18n_clients/km_pays.po`).

Ordre conseillé : parties 1 et 2 d'abord (ce que chaque client voit sur ses documents
et sur l'accueil), puis la partie 3.

**0 / 689 textes relus.**

## 1. Documents imprimés et pages Chantrea

Libellés des devis, factures, rapports d'intervention et pages du parc matériel. À corriger dans le gabarit XML du module indiqué.

0 / 64 textes relus.

| Statut | Khmer | Anglais | Module(s) |
|---|---|---|---|
| ⏳ à relire | វិក្កយបត្របណ្ដោះអាសន្ន | PRO-FORMA INVOICE | chantrea_kh_facture |
| ⏳ à relire | ប័ណ្ណបញ្ជាទិញ | SALES ORDER | chantrea_kh_facture |
| ⏳ à relire | សម្រង់តម្លៃ | QUOTATION | chantrea_kh_facture |
| ⏳ à relire | បានលុបចោល | CANCELLED | chantrea_kh_facture |
| ⏳ à relire | លេខប័ណ្ណបញ្ជាទិញ | Order No. | chantrea_kh_facture |
| ⏳ à relire | លេខសម្រង់តម្លៃ | Quotation No. | chantrea_kh_facture |
| ⏳ à relire | កាលបរិច្ឆេទ | Date | account, chantrea_kh_facture, contract, helpdesk_mgmt_timesheet |
| ⏳ à relire | មានសុពលភាពរហូតដល់ | Valid until | chantrea_kh_facture |
| ⏳ à relire | ឯកសារយោង | Reference | account, account_payment, chantrea_kh_facture, contract |
| ⏳ à relire | ល.រ | No. | chantrea_kh_facture |
| ⏳ à relire | បរិយាយមុខទំនិញ | Description | chantrea_kh_facture |
| ⏳ à relire | បរិមាណ | Quantity | account, chantrea_kh_facture, contract, sale |
| ⏳ à relire | ថ្លៃឯកតា | Unit price | chantrea_kh_facture |
| ⏳ à relire | បញ្ចុះតម្លៃ % | Discount % | chantrea_kh_facture |
| ⏳ à relire | ថ្លៃទំនិញ | Amount | chantrea_kh_facture |
| ⏳ à relire | ហត្ថលេខា ឈ្មោះ និងកាលបរិច្ឆេទ អ្នកទិញ (យល់ព្រម) | Customer's signature, name and date (accepted) | chantrea_kh_facture |
| ⏳ à relire | ហត្ថលេខា និងឈ្មោះអ្នកលក់ | Seller's signature and name | chantrea_kh_facture |
| ⏳ à relire | លិខិតឥណទាន | CREDIT NOTE | chantrea_kh_facture |
| ⏳ à relire | វិក្កយបត្រអាករ | TAX INVOICE | chantrea_kh_facture |
| ⏳ à relire | វិក្កយបត្រពាណិជ្ជកម្ម | COMMERCIAL INVOICE | chantrea_kh_facture |
| ⏳ à relire | សេចក្តីព្រាង | DRAFT | chantrea_kh_facture |
| ⏳ à relire | លេខលិខិតឥណទាន | Credit note No. | chantrea_kh_facture |
| ⏳ à relire | លេខរៀងវិក្កយបត្រ | Invoice No. | chantrea_kh_facture |
| ⏳ à relire | ថ្ងៃផុតកំណត់ទូទាត់ | Due date | chantrea_kh_facture |
| ⏳ à relire | វិក្កយបត្រដើម | Original invoice | chantrea_kh_facture |
| ⏳ à relire | សេចក្តីយោងការទូទាត់ | Payment reference | chantrea_kh_facture |
| ⏳ à relire | គណនីធនាគារ | Bank account | chantrea_kh_facture |
| ⏳ à relire | ហត្ថលេខា និងឈ្មោះអ្នកទិញ | Customer's signature and name | chantrea_kh_facture |
| ⏳ à relire | ចំណាំ៖ ច្បាប់ដើមសម្រាប់អ្នកទិញ ច្បាប់ចម្លងសម្រាប់អ្នកលក់ | Note: original for the customer, copy for the seller | chantrea_kh_facture |
| ⏳ à relire | លេខអត្តសញ្ញាណកម្ម អតប | VATTIN | chantrea_kh_facture |
| ⏳ à relire | ទំព័រ | Page | chantrea_kh_facture |
| ⏳ à relire | ឈ្មោះក្រុមហ៊ុន ឬ អតិថិជន | Company or customer name | chantrea_kh_facture |
| ⏳ à relire | អាសយដ្ឋាន | Address | chantrea_kh_facture |
| ⏳ à relire | ទូរស័ព្ទលេខ | Telephone No. | chantrea_kh_facture |
| ⏳ à relire | សរុប | Sub-total | chantrea_kh_facture |
| ⏳ à relire | អាករ | (valeur variable : groupe['group_name']) | chantrea_kh_facture |
| ⏳ à relire | សរុបរួម | Grand total | chantrea_kh_facture |
| ⏳ à relire | សរុបមិនរួមអាករ ជាប្រាក់រៀល | Sub-total in riels | chantrea_kh_facture |
| ⏳ à relire | អាករ ជាប្រាក់រៀល | Tax in riels | chantrea_kh_facture |
| ⏳ à relire | សរុបរួមជាប្រាក់រៀល | Grand total in riels | chantrea_kh_facture |
| ⏳ à relire | សរុបរួមជាប្រាក់ដុល្លារអាមេរិក | Grand total in US dollars | chantrea_kh_facture |
| ⏳ à relire | អត្រាប្តូរប្រាក់ | Exchange rate | chantrea_kh_facture |
| ⏳ à relire | អគ្គនាយកដ្ឋានពន្ធដារ | GDT | chantrea_kh_facture |
| ⏳ à relire | ធនាគារជាតិនៃកម្ពុជា | NBC | chantrea_kh_facture |
| ⏳ à relire | បញ្ចូលដោយដៃ | manual entry | chantrea_kh_facture |
| ⏳ à relire | អត្រាបណ្ដោះអាសន្ន សម្រាប់ជាព័ត៌មានប៉ុណ្ណោះ | Provisional rate, for information only | chantrea_kh_facture |
| ⏳ à relire | មិនទាន់មានអត្រាប្តូរប្រាក់ផ្លូវការ | Official exchange rate not yet available | chantrea_kh_facture |
| ⏳ à relire | របាយការណ៍សេវាកម្មនៅទីតាំង | ON-SITE SERVICE REPORT | chantrea_parc |
| ⏳ à relire | មិនទាន់បញ្ចប់ | NOT COMPLETED | chantrea_parc |
| ⏳ à relire | លេខរបាយការណ៍ | Report No. | chantrea_parc |
| ⏳ à relire | ទីតាំង | Site | chantrea_parc, home |
| ⏳ à relire | មកដល់ | Arrival | chantrea_parc |
| ⏳ à relire | បញ្ចប់ | End | chantrea_parc |
| ⏳ à relire | អ្នកបច្ចេកទេស | Technician | chantrea_parc |
| ⏳ à relire | សំណើជំនួយ | Ticket | chantrea_parc, fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | ឧបករណ៍ពាក់ព័ន្ធ | Equipment concerned | chantrea_parc, home |
| ⏳ à relire | ឧបករណ៍ | Equipment | chantrea_parc, home |
| ⏳ à relire | ម៉ាក និងម៉ូដែល | Brand and model | chantrea_parc, home |
| ⏳ à relire | លេខស៊េរី | Serial number | chantrea_parc, home |
| ⏳ à relire | ការងារដែលបានស្នើ | Work requested | chantrea_parc |
| ⏳ à relire | ការងារដែលបានធ្វើ | Work done | chantrea_parc, home |
| ⏳ à relire | ហត្ថលេខាអតិថិជន | Customer's signature | chantrea_parc |
| ⏳ à relire | មិនទាន់ចុះហត្ថលេខា | Not signed yet | chantrea_parc |
| ⏳ à relire | កញ្ចប់ថែទាំព័ត៌មានវិទ្យាប្រចាំខែ (#START# – #END#) | Monthly IT maintenance plan | chantrea_portail |

## 2. Modules Chantrea

Catégories de tickets, courriels, accueil de l'espace client… À corriger dans `addons/<module>/i18n/km.po`.

0 / 65 textes relus.

| Statut | Khmer | Anglais | Module(s) |
|---|---|---|---|
| ⏳ à relire | ទាញយករបាយការណ៍ (PDF) | Download the report (PDF) | home |
| ⏳ à relire | ម៉ាក | Brand | home |
| ⏳ à relire | ប្រភេទ | Category | account, helpdesk_mgmt, home |
| ⏳ à relire | កិច្ចសន្យា | Contract | contract, home |
| ⏳ à relire | អតិថិជន | Customer | account, helpdesk_mgmt, home |
| ⏳ à relire | ហត្ថលេខាអតិថិជន | Customer signature | home |
| ⏳ à relire | ឈ្មោះសំរាប់បង្ហាញ | Display Name | home |
| ⏳ à relire | ផុតកំណត់ក្នុងរយៈពេល ៦០ ថ្ងៃ | Ends within 60 days | home |
| ⏳ à relire | ផុតកំណត់ | Expired | home, sale |
| ⏳ à relire | ជញ្ជាំងភ្លើង (Firewall) | Firewall | home |
| ⏳ à relire | ការចុះជួសជុល | Interventions | home |
| ⏳ à relire | អាជ្ញាប័ណ្ណ | License | home |
| ⏳ à relire | ម៉ូដែល | Model | home |
| ⏳ à relire | មិនទាន់មានឧបករណ៍ត្រូវបានកត់ត្រានៅឡើយទេ។ | No equipment recorded yet. | home |
| ⏳ à relire | មិនមានការចុះជួសជុលសម្រាប់ឧបករណ៍នេះទេ។ | No intervention for this equipment. | home |
| ⏳ à relire | មិនមានសំណើជំនួយសម្រាប់ឧបករណ៍នេះទេ។ | No ticket for this equipment. | home |
| ⏳ à relire | មិនទាន់បំពេញនៅឡើយទេ។ | Not filled in yet. | home |
| ⏳ à relire | មិនទាន់ចុះហត្ថលេខានៅឡើយទេ។ | Not signed yet. | home |
| ⏳ à relire | កាលបរិច្ឆេទទិញ | Purchase date | home |
| ⏳ à relire | ម៉ាស៊ីនមេ (Server) | Server | home |
| ⏳ à relire | ម៉ាស៊ីនមេ បណ្ដាញ កុំព្យូទ័រ និងអាជ្ញាប័ណ្ណ ព្រមទាំងការធានារបស់វា | Servers, network, workstations and licences, with their warranty | home |
| ⏳ à relire | ហត្ថលេខា | Signature | home, sale |
| ⏳ à relire | ចុះហត្ថលេខាដោយ | Signed by | home |
| ⏳ à relire | ឧបករណ៍ផ្ទុកទិន្នន័យ | Storage | home |
| ⏳ à relire | សំណើជំនួយ | Tickets | helpdesk_mgmt, home |
| ⏳ à relire | ឧបករណ៍បម្រុងថាមពល (UPS) | UPS | home |
| ⏳ à relire | ក្នុងការធានា | Under warranty | home |
| ⏳ à relire | មិនស្គាល់ | Unknown | home |
| ⏳ à relire | ការធានា | Warranty | home |
| ⏳ à relire | ថ្ងៃផុតការធានា | Warranty end | home |
| ⏳ à relire | ការធានាជិតផុតកំណត់ | Warranty ends soon | home |
| ⏳ à relire | ការធានាផុតកំណត់ | Warranty expired | home |
| ⏳ à relire | ស្ថានភាពការធានា | Warranty status | home |
| ⏳ à relire | មិនស្គាល់ការធានា | Warranty unknown | home |
| ⏳ à relire | កុំព្យូទ័រការិយាល័យ | Workstation | home |
| ⏳ à relire | ឧបករណ៍របស់លោកអ្នក | Your equipment | home |
| ⏳ à relire | សួស្តី Dara , យើងបានទទួលសំណើរបស់លោកអ្នក Printer out of order ក្រោមលេខ HT00001 ហើយ។ អ្នកបច្ចេកទេសនឹងឆ្លើយតបទៅលោកអ្នកឆាប់ៗនេះ។ លោកអ្នកអាចតាមដានសំណើនេះ និងឆ្លើយតបនៅក្នុងតំបន់អតិថិជនរបស់លោកអ្នក។ មើលសំណើរបស់ខ្ញុំ Chantrea Systems | Hello Dara , We have received your request Printer out of order under number HT00001 . A technician will get back to you as soon as possible. You can follow this request and reply to it in your customer area. View my request Chantrea Systems | home |
| ⏳ à relire | ការបម្រុងទុក និងទិន្នន័យ | Backup and data | home |
| ⏳ à relire | ផ្នែកជំនួយ Chantrea Systems | Chantrea Systems support | home |
| ⏳ à relire | អ៊ីមែល និងគណនីអ្នកប្រើប្រាស់ | Email and user accounts | home |
| ⏳ à relire | ផ្នែករឹង និងឧបករណ៍ | Hardware and devices | home |
| ⏳ à relire | ការចុះទិន្នានុប្បរត្ត | Journal Entry | home |
| ⏳ à relire | កញ្ចប់ថែទាំព័ត៌មានវិទ្យាប្រចាំខែ | Monthly IT maintenance plan | home |
| ⏳ à relire | បណ្ដាញ អ៊ីនធឺណិត និង Wi-Fi | Network, Internet and Wi-Fi | home |
| ⏳ à relire | សំណើផ្សេងទៀត | Other request | home |
| ⏳ à relire | សុវត្ថិភាព និងមេរោគ | Security and viruses | home |
| ⏳ à relire | កម្មវិធី និងសូហ្វវែរ | Software and applications | home |
| ⏳ à relire | សំណើរបស់លោកអ្នក {{ object.number }} ត្រូវបានទទួលហើយ | Your request {{ object.number }} has been received | home |
| ⏳ à relire | ស្នើសុំជំនួយ | Ask for help | home |
| ⏳ à relire | យល់ព្រម និងចុះហត្ថលេខាតាមអនឡាញ | Accept and sign online | home |
| ⏳ à relire | កិច្ចសន្យាកំពុងមានសុពលភាព | Active contracts | home |
| ⏳ à relire | ការចុះជួសជុលទាំងអស់ ព្រមទាំងរបាយការណ៍ដែលបានចុះហត្ថលេខា៖ | All interventions, with their signed reports: | home |
| ⏳ à relire | ចំនួនត្រូវបង់៖ | Amount due: | home |
| ⏳ à relire | តាមដាន និងឆ្លើយតបសំណើជំនួយរបស់លោកអ្នក | Follow and answer your support tickets | home |
| ⏳ à relire | សួស្តី | Hello | home |
| ⏳ à relire | ការចុះជួសជុលកំពុងដំណើរការ | Interventions in progress | home |
| ⏳ à relire | វិក្កយបត្រត្រូវបង់ | Invoices to pay | account_payment, home |
| ⏳ à relire | ការថែទាំ និងសេវាកម្ម | Maintenance and services | home |
| ⏳ à relire | គ្មានអ្វីត្រូវបង់ទេ | Nothing to pay | home |
| ⏳ à relire | សំណើជំនួយកំពុងបើក | Open requests | home |
| ⏳ à relire | សម្រង់តម្លៃត្រូវពិនិត្យ | Quotations to review | home, sale |
| ⏳ à relire | ម៉ាស៊ីនមេ បណ្តាញ កុំព្យូទ័រ អាជ្ញាប័ណ្ណ | Servers, network, workstations, licences | home |
| ⏳ à relire | ការធានាដែលនឹងផុតកំណត់ក្នុងរយៈពេល 60 ថ្ងៃ៖ | Warranties ending within 60 days: | home |
| ⏳ à relire | ទិដ្ឋភាពរួមនៃប្រព័ន្ធព័ត៌មានវិទ្យារបស់លោកអ្នក៖ សំណើជំនួយ ការចុះជួសជុល ឧបករណ៍ និងវិក្កយបត្រ។ | Your IT at a glance: requests, interventions, equipment and invoices. | home |
| ⏳ à relire | គណនីរបស់លោកអ្នក | Your account | home |

## 3. Textes d'Odoo et de l'OCA vus par les clients

Pages standard de l'espace client, fenêtres et courriels d'Odoo et des modules OCA. À corriger dans `addons/chantrea_portail/i18n_clients/km.po` (la colonne indique le module d'origine).

0 / 560 textes relus.

| Statut | Khmer | Anglais | Module(s) |
|---|---|---|---|
| ⏳ à relire | ជូនចំពោះ Brandon Freeman ( Azure Interior ), Azure Interior , Brandon Freeman , នេះជា វិក្កយបត្រ INV/2021/05/0005 វិក្កយបត្រ (ឯកសារយោង៖ SUB003 ) ចំនួនទឹកប្រាក់ $ 143,750.00 ពី YourCompany . វិក្កយបត្រនេះត្រូវបានបង់រួចហើយ។ សូមទូទាត់ប្រាក់ឱ្យបានឆាប់តាមដែលអាចធ្វើបាន។ សូមប្រើសេចក្តីយោងខាងក្រោមនៅពេលទូទាត់៖ INV/2021/05/0005 ទៅគណនី . បន្ថែម៖ លោកអ្នកអាចពិនិត្យតារាងម៉ោងធ្វើការ នៅក្នុងតំបន់អតិថិជន។ ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ -- Mitchell Admin | Dear Brandon Freeman ( Azure Interior ), Azure Interior , Brandon Freeman , Here is your invoice INV/2021/05/0005 invoice (with reference: SUB003 ) amounting in $ 143,750.00 from YourCompany . This invoice is already paid. Please remit payment at your earliest convenience. Please use the following communication for your payment: INV/2021/05/0005 on the account . PS: you can review your timesheets from the portal. Do not hesitate to contact us if you have any questions. -- Mitchell Admin | account |
| ⏳ à relire | ជូនចំពោះ Brandon Freeman ( Azure Interior ), Brandon Freeman , នេះជា លិខិតឥណទាន RINV/2021/05/0001 លិខិតឥណទាន (ឯកសារយោង៖ SUB003 ) ចំនួនទឹកប្រាក់ $ 143,750.00 ពី YourCompany . ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ -- Mitchell Admin | Dear Brandon Freeman ( Azure Interior ), Brandon Freeman , Here is your credit note RINV/2021/05/0001 credit note (with reference: SUB003 ) amounting in $ 143,750.00 from YourCompany . Do not hesitate to contact us if you have any questions. -- Mitchell Admin | account |
| ⏳ à relire | ជូនចំពោះ Azure Interior សូមអរគុណសម្រាប់ការទូទាត់។ នេះជាបង្កាន់ដៃទូទាត់របស់លោកអ្នក BNK1-2021-05-0002 ចំនួនទឹកប្រាក់ $ 10.00 ពី YourCompany . ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ ដោយក្តីគោរព, -- Mitchell Admin | Dear Azure Interior Thank you for your payment. Here is your payment receipt BNK1-2021-05-0002 amounting to $ 10.00 from YourCompany . Do not hesitate to contact us if you have any questions. Best regards, -- Mitchell Admin | account |
| ⏳ à relire | ទាញយក | Download | account, mail |
| ⏳ à relire | កំពុងរង់ចាំការទូទាត់ | Waiting for Payment | account |
| ⏳ à relire | បានលុបចោល | Cancelled | account, fieldservice, helpdesk_mgmt, sale, sale_stock |
| ⏳ à relire | ឬ | or | account, portal |
| ⏳ à relire | ពន្ធ | Taxes | account, sale |
| ⏳ à relire | ថ្មី | New | account, fieldservice, helpdesk_mgmt, mail, sale |
| ⏳ à relire | ចំនួនទឹកប្រាក់ | Amount | account, account_payment, sale |
| ⏳ à relire | ការពិពណ៌នា | Description | account, contract, fieldservice_portal, helpdesk_mgmt, helpdesk_mgmt_timesheet, portal |
| ⏳ à relire | កាលបរិច្ឆេទវិក្កយបត្រ | Invoice Date | account |
| ⏳ à relire | តម្លៃឯកតា | Unit Price | account, contract, sale |
| ⏳ à relire | ថ្ងៃផុតកំណត់៖ | Due Date: | account |
| ⏳ à relire | ថ្ងៃផុតកំណត់ | Due Date | account |
| ⏳ à relire | កាលបរិច្ឆេទវិក្កយបត្រ៖ | Invoice Date: | account |
| ⏳ à relire | សរុប | Total | account, sale |
| ⏳ à relire | ប្រភេទ៖ | Type: | account, base, mail |
| ⏳ à relire | អ្នកគ្រប់គ្រង | Administrator | account |
| ⏳ à relire | ចំនួនត្រូវបង់ | Amount Due | account |
| ⏳ à relire | វិក្កយបត្រទិញ | Bills | account |
| ⏳ à relire | ទីក្រុង | City | account, portal |
| ⏳ à relire | បិទ | Close | account, account_payment, portal, sale, web |
| ⏳ à relire | ប្រវត្តិទំនាក់ទំនង | Communication history | account, helpdesk_mgmt, sale |
| ⏳ à relire | ទំនាក់ទំនង | Contact | account, contract, portal |
| ⏳ à relire | កិច្ចសន្យា | Contracts | account, contract |
| ⏳ à relire | ប្រទេស | Country | account, portal |
| ⏳ à relire | អតិថិជន៖ | Customer: | account, contract |
| ⏳ à relire | បោះបង់ | Discard | account, auth_passkey_portal, auth_totp, portal |
| ⏳ à relire | បញ្ចុះតម្លៃ (%) | Discount (%) | account, contract |
| ⏳ à relire | តាមដាន ទាញយក ឬបង់វិក្កយបត្ររបស់យើង | Follow, download or pay our invoices | account |
| ⏳ à relire | តាមដាន ទាញយក ឬបង់វិក្កយបត្ររបស់លោកអ្នក | Follow, download or pay your invoices | account |
| ⏳ à relire | ដាក់ជាក្រុមតាម | Group By | account |
| ⏳ à relire | វិក្កយបត្រលេខ | Invoice # | account |
| ⏳ à relire | វិក្កយបត្រ | Invoices & Bills | account, account_payment |
| ⏳ à relire | ស្លាកសញ្ញា | Logo | account, web |
| ⏳ à relire | ឈ្មោះ | Name | account, auth_passkey_portal, auth_signup, base, contract, fieldservice_portal |
| ⏳ à relire | គ្មាន | None | account, fieldservice_portal, helpdesk_mgmt, mail |
| ⏳ à relire | លេខ | Number | account, helpdesk_mgmt |
| ⏳ à relire | បើក | Open | account, fieldservice_portal, mail, portal |
| ⏳ à relire | វិក្កយបត្ររបស់យើង | Our Invoices | account |
| ⏳ à relire | បង់ប្រាក់ | Pay | account, account_payment |
| ⏳ à relire | ផលិតផល | Products | account, sale |
| ⏳ à relire | បរិមាណ៖ | Quantity: | account |
| ⏳ à relire | បដិសេធ | Reject | account, sale |
| ⏳ à relire | បានបដិសេធ | Rejected | account, helpdesk_mgmt |
| ⏳ à relire | អ្នកលក់ | Salesperson | account, sale |
| ⏳ à relire | ស្ថានភាព | Status | account |
| ⏳ à relire | ប្រធានបទ | Subject | account, helpdesk_mgmt |
| ⏳ à relire | ប្រភេទ | Type | account, base, fieldservice_portal |
| ⏳ à relire | តម្លៃឯកតា៖ | Unit Price: | account |
| ⏳ à relire | ឯកតា | Units | account, uom |
| ⏳ à relire | អាករលើតម្លៃបន្ថែម ១០% | VAT 10% | account |
| ⏳ à relire | វិក្កយបត្ររបស់លោកអ្នក | Your Invoices | account |
| ⏳ à relire | {{ object.company_id.name }} លិខិតឥណទាន (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} Credit Note (Ref {{ object.name or 'n/a' }}) | account |
| ⏳ à relire | {{ object.company_id.name }} វិក្កយបត្រ (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} Invoice (Ref {{ object.name or 'n/a' }}) | account |
| ⏳ à relire | {{ object.company_id.name }} បង្កាន់ដៃទូទាត់ (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} Payment Receipt (Ref {{ object.name or 'n/a' }}) | account |
| ⏳ à relire | សេចក្តីយោង៖ | Communication: | account_payment |
| ⏳ à relire | បង់ប្រាក់ឥឡូវនេះ | Pay Now | account_payment, sale |
| ⏳ à relire | បង់ប្រាក់ឥឡូវនេះ | Pay now | account_payment |
| ⏳ à relire | បន្ថែម Passkey | Add Passkey | auth_passkey, auth_passkey_portal |
| ⏳ à relire | កូនសោ Passkey | Passkeys | auth_passkey, auth_passkey_portal |
| ⏳ à relire | ប្រើ Passkey | Use a Passkey | auth_passkey |
| ⏳ à relire | គណនីរបស់លោកអ្នក Marc Demo ជូនចំពោះ Marc Demo , សូមស្វាគមន៍មកកាន់ YourCompany – តំបន់អតិថិជន! គណនីមួយត្រូវបានបង្កើតសម្រាប់លោកអ្នក ដោយប្រើឈ្មោះចូលខាងក្រោម៖ demo សូមចុចប៊ូតុងខាងក្រោម ដើម្បីជ្រើសរើសពាក្យសម្ងាត់ និងបើកដំណើរការគណនីរបស់លោកអ្នក។ បើកដំណើរការគណនី សូមស្វាគមន៍មកកាន់តំបន់អតិថិជនរបស់យើង។ YourCompany +1 650-123-4567 / info@yourcompany.com / http://www.example.com ដំណើរការដោយ Odoo | Your Account Marc Demo Dear Marc Demo , Welcome to YourCompany 's Portal! An account has been created for you with the following login: demo Click on the button below to pick a password and activate your account. Activate Account Welcome to our company's portal. YourCompany +1 650-123-4567 / info@yourcompany.com / http://www.example.com Powered by Odoo | auth_signup |
| ⏳ à relire | គណនីរបស់លោកអ្នក Marc Demo ជូនចំពោះ Marc Demo , គណនីរបស់លោកអ្នកត្រូវបានបង្កើតដោយជោគជ័យ! ឈ្មោះចូលរបស់លោកអ្នកគឺ mark.brown23@example.com ដើម្បីចូលប្រើគណនីរបស់លោកអ្នក សូមប្រើតំណខាងក្រោម៖ ចូលទៅគណនីរបស់ខ្ញុំ សូមអរគុណ, -- Mitchell Admin YourCompany +1 650-123-4567 / info@yourcompany.com / http://www.example.com ដំណើរការដោយ Odoo | Your Account Marc Demo Dear Marc Demo , Your account has been successfully created! Your login is mark.brown23@example.com To gain access to your account, you can use the following link: Go to My Account Thanks, -- Mitchell Admin YourCompany +1 650-123-4567 / info@yourcompany.com / http://www.example.com Powered by Odoo | auth_signup |
| ⏳ à relire | ត្រឡប់ទៅការចូលគណនី | Back to Login | auth_signup |
| ⏳ à relire | អ៊ីមែល | Email | auth_signup, portal, web |
| ⏳ à relire | ពាក្យសម្ងាត់ | Password | auth_signup, portal, web |
| ⏳ à relire | ដំណើរការដោយ | Powered by | auth_signup, mail, portal |
| ⏳ à relire | កំណត់ពាក្យសម្ងាត់ឡើងវិញ | Reset Password | auth_signup |
| ⏳ à relire | សូមស្វាគមន៍មកកាន់ {{ object.company_id.name }}! | Welcome to {{ object.company_id.name }}! | auth_signup |
| ⏳ à relire | គណនីរបស់លោកអ្នកនៅ {{ object.company_id.name }} | Your account at {{ object.company_id.name }} | auth_signup |
| ⏳ à relire | មិនទាន់បើកការផ្ទៀងផ្ទាត់ពីរជំហាន | Two-factor authentication not enabled | auth_totp_portal |
| ⏳ à relire | បើកការផ្ទៀងផ្ទាត់ពីរជំហាន | Enable two-factor authentication | auth_totp_portal |
| ⏳ à relire | ការផ្ទៀងផ្ទាត់ពីរជំហាន | Two-factor authentication | auth_totp_portal |
| ⏳ à relire | អ៊ីមែល៖ | Email: | base |
| ⏳ à relire | ទាំងអស់ | All | account, base, contract, fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | ដោយ | By | base, helpdesk_mgmt |
| ⏳ à relire | ប្តូរពាក្យសម្ងាត់ | Change Password | base, portal |
| ⏳ à relire | កាលបរិច្ឆេទបង្កើត | Create Date | base, helpdesk_mgmt |
| ⏳ à relire | រួចរាល់ | Done | base, helpdesk_mgmt, mail |
| ⏳ à relire | បញ្ចូលពាក្យសម្ងាត់របស់លោកអ្នក | Enter your password | base, web |
| ⏳ à relire | កាលបរិច្ឆេទផុតកំណត់ | Expiration Date | base, portal |
| ⏳ à relire | ប្រវត្តិ | History | base, fieldservice_portal |
| ⏳ à relire | ម៉ោង | Hours | base, uom |
| ⏳ à relire | ចាកចេញពីឧបករណ៍ទាំងអស់ | Log out from all devices | base, portal |
| ⏳ à relire | ឈ្មោះ៖ | Name: | base |
| ⏳ à relire | ពាក្យសម្ងាត់ថ្មី | New Password | base |
| ⏳ à relire | ស្វែងរក | Search | base, portal |
| ⏳ à relire | តារាងម៉ោងធ្វើការ | Timesheets | base, helpdesk_mgmt_timesheet |
| ⏳ à relire | លេខអត្តសញ្ញាណកម្ម អតប | VAT | base, portal |
| ⏳ à relire | សួស្តី , កិច្ចសន្យាថ្មីមួយត្រូវបានបង្កើត៖ &nbsp;&nbsp; ឯកសារយោង &nbsp;&nbsp;កិច្ចសន្យា៖ &nbsp;&nbsp;ថ្ងៃចាប់ផ្តើមកិច្ចសន្យា៖ &nbsp;&nbsp;អ្នកទំនាក់ទំនងរបស់លោកអ្នក៖ &nbsp;&nbsp;អ្នកទំនាក់ទំនងរបស់លោកអ្នក៖ ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ សូមអរគុណដែលបានជ្រើសរើស ! ទូរស័ព្ទ៖ គេហទំព័រ៖ មើលកិច្ចសន្យា | Hello , A new contract has been created: &nbsp;&nbsp; REFERENCES &nbsp;&nbsp;Contract: &nbsp;&nbsp;Contract Start Date: &nbsp;&nbsp;Your Contact: &nbsp;&nbsp;Your Contact: If you have any questions, do not hesitate to contact us. Thank you for choosing ! Phone: Web: View contract | contract |
| ⏳ à relire | មើលព័ត៌មានលម្អិត | View Details | contract, sale |
| ⏳ à relire | កិច្ចសន្យា៖ | Contract: | contract |
| ⏳ à relire | ថ្ងៃបញ្ចប់ | Date end | contract |
| ⏳ à relire | កាលបរិច្ឆេទវិក្កយបត្របន្ទាប់ | Date of Next Invoice | contract |
| ⏳ à relire | អ្នកទទួលខុសត្រូវ៖ | Responsible: | contract, sign_oca |
| ⏳ à relire | សេចក្តីយោង | Communication | contract |
| ⏳ à relire | កិច្ចសន្យាលេខ | Contract # | contract |
| ⏳ à relire | កាលបរិច្ឆេទវិក្កយបត្របន្ទាប់ | Date of next invoice | contract |
| ⏳ à relire | តាមដានសេវាកម្មដែលយើងចេញវិក្កយបត្រជូនលោកអ្នក | Follow the services we invoice you for | contract |
| ⏳ à relire | តាមដានសេវាកម្មដែលលោកអ្នកចេញវិក្កយបត្រជូនយើង | Follow the services you invoice us for | contract |
| ⏳ à relire | ខែ | Month(s) | contract |
| ⏳ à relire | កិច្ចសន្យារបស់យើង | Our Contracts | contract |
| ⏳ à relire | តម្លៃឯកតា | Price unit | contract |
| ⏳ à relire | ភាពញឹកញាប់ | Recurrence | contract |
| ⏳ à relire | អ្នកទទួលខុសត្រូវ | Responsible | contract |
| ⏳ à relire | សរុបរង | Sub Total | contract |
| ⏳ à relire | លេខអត្តសញ្ញាណកម្ម អតប៖ | VAT: | contract |
| ⏳ à relire | កិច្ចសន្យារបស់លោកអ្នក | Your Contracts | contract |
| ⏳ à relire | {{ object.company_id.name }} កិច្ចសន្យា (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} Contract (Ref {{ object.name or 'n/a' }}) | contract |
| ⏳ à relire | បានបញ្ចប់ | Completed | fieldservice |
| ⏳ à relire | ការចុះជួសជុល | FSM Orders | fieldservice, fieldservice_portal |
| ⏳ à relire | ទីតាំង | Location | fieldservice, fieldservice_portal |
| ⏳ à relire | ដំណាក់កាល | Stage | fieldservice, fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | មកដល់ទីតាំង៖ | Arrival On Site: | fieldservice_portal |
| ⏳ à relire | ទីក្រុង៖ | City: | fieldservice_portal |
| ⏳ à relire | ប្រទេស៖ | Country: | fieldservice_portal |
| ⏳ à relire | ប្រភេទការងារ៖ | Work Type: | fieldservice_portal |
| ⏳ à relire | ទីតាំង៖ | Location: | fieldservice_portal, mail |
| ⏳ à relire | ដំណាក់កាល៖ | Stage: | fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | មិនទាន់ចាប់ផ្តើម | Not started yet | fieldservice_portal |
| ⏳ à relire | មិនមានការចុះជួសជុលក្នុងគណនីរបស់លោកអ្នកទេ។ | There are no Work Orders in your account. | fieldservice_portal |
| ⏳ à relire | មើលការចុះជួសជុលរបស់លោកអ្នក | View your fieldservice orders | fieldservice_portal |
| ⏳ à relire | ការចុះជួសជុល | Work Orders | fieldservice_portal |
| ⏳ à relire | សួស្តី , សំណើជំនួយ បានប្តូរដំណាក់កាលទៅ . | Hello , The ticket stage has changed to . | helpdesk_mgmt |
| ⏳ à relire | សួស្តី , សំណើជំនួយ ត្រូវបានបិទហើយ។ | Hello , The ticket has been closed. | helpdesk_mgmt |
| ⏳ à relire | អ្នកទទួលបន្ទុក | Assignee | helpdesk_mgmt |
| ⏳ à relire | ប្រភេទ៖ | Category: | helpdesk_mgmt |
| ⏳ à relire | កាលបរិច្ឆេទបង្កើត៖ | Create Date: | helpdesk_mgmt |
| ⏳ à relire | បច្ចុប្បន្នភាពចុងក្រោយ៖ | Last Stage Update: | helpdesk_mgmt |
| ⏳ à relire | ភ្ជាប់ឯកសារ | Add Attachments | helpdesk_mgmt |
| ⏳ à relire | កំពុងរង់ចាំ | Awaiting | helpdesk_mgmt |
| ⏳ à relire | កាលបរិច្ឆេទបិទ | Close Date | helpdesk_mgmt |
| ⏳ à relire | ដំណាក់កាលបច្ចុប្បន្នរបស់សំណើ | Current stage of the ticket | helpdesk_mgmt |
| ⏳ à relire | ដំណាក់កាលបច្ចុប្បន្នរបស់សំណើនេះ | Current stage of this ticket | helpdesk_mgmt |
| ⏳ à relire | តាមដាន និងផ្តល់មតិលើសំណើជំនួយរបស់លោកអ្នក | Follow and comment your helpdesk tickets | helpdesk_mgmt |
| ⏳ à relire | កំពុងដំណើរការ | In Progress | helpdesk_mgmt |
| ⏳ à relire | បច្ចុប្បន្នភាពចុងក្រោយ | Last Stage Update | helpdesk_mgmt |
| ⏳ à relire | ផ្ញើសំណើជំនួយថ្មី | Send a new ticket | helpdesk_mgmt |
| ⏳ à relire | ផ្ញើសំណើ | Submit Ticket | helpdesk_mgmt |
| ⏳ à relire | សំណើជំនួយ {{object.number}} ត្រូវបានបិទហើយ។ | The ticket {{object.number}} has been closed. | helpdesk_mgmt |
| ⏳ à relire | សំណើជំនួយ {{object.number}} បានប្តូរដំណាក់កាល។ | The ticket {{object.number}} stage has changed. | helpdesk_mgmt |
| ⏳ à relire | ចំណងជើង | Title | helpdesk_mgmt |
| ⏳ à relire | កាលបរិច្ឆេទ៖ | Date: | mail, sale, sale_stock |
| ⏳ à relire | មតិ | Feedback | mail, sale |
| ⏳ à relire | មតិ៖ | Feedback: | mail |
| ⏳ à relire | ប្រើចុងក្រោយ | Last Used | auth_passkey_portal, mail |
| ⏳ à relire | មិនមានវិធីទូទាត់ទេ | No payment method available | payment |
| ⏳ à relire | លេខកូដប្រៃសណីយ៍ | Zip Code | payment, portal |
| ⏳ à relire | ១. បញ្ចូលពាក្យសម្ងាត់ ដើម្បីបញ្ជាក់ថាលោកអ្នកជាម្ចាស់គណនីនេះ | 1. Enter your password to confirm you own this account | portal |
| ⏳ à relire | គណនីរបស់ខ្ញុំ | My Account | portal |
| ⏳ à relire | ចាកចេញ | Logout | portal |
| ⏳ à relire | កែប្រែព័ត៌មាន | Edit information | portal |
| ⏳ à relire | ប្រទេស... | Country... | portal |
| ⏳ à relire | ខេត្ត / រដ្ឋ... | State / Province... | portal |
| ⏳ à relire | ច្រោះតាម៖ | Filter By: | portal |
| ⏳ à relire | ដាក់ជាក្រុមតាម៖ | Group By: | portal |
| ⏳ à relire | តម្រៀបតាម៖ | Sort By: | portal |
| ⏳ à relire | បន្ថែម លុប ឬកែប្រែអាសយដ្ឋានរបស់លោកអ្នក | Add, remove or modify your addresses | portal |
| ⏳ à relire | អាសយដ្ឋាន | Addresses | portal |
| ⏳ à relire | ផ្ទះលេខ បន្ទប់ ។ល។ | Apartment, suite, etc. | portal |
| ⏳ à relire | តើលោកអ្នកប្រាកដថាចង់ធ្វើដូច្នេះមែនទេ? | Are you sure you want to do this? | portal |
| ⏳ à relire | កំណត់ការចូលគណនី និងសុវត្ថិភាព | Configure your connection parameters | portal |
| ⏳ à relire | ការចូលគណនី និងសុវត្ថិភាព | Connection & Security | portal |
| ⏳ à relire | លុបគណនី | Delete Account | portal |
| ⏳ à relire | ព័ត៌មានលម្អិត | Details | portal |
| ⏳ à relire | បិទគណនីរបស់លោកអ្នក ដោយមិនអាចចូលបានទៀតឡើយ។ សកម្មភាពនេះមិនអាចត្រឡប់វិញបានទេ។ | Disable your account, preventing any further login. This action cannot be undone. | portal |
| ⏳ à relire | ត្រឡប់ក្រោយ | Go Back | portal |
| ⏳ à relire | ទំព័រដើម | Home | http_routing, portal |
| ⏳ à relire | គណនីរបស់ខ្ញុំ | My account | portal |
| ⏳ à relire | ពាក្យសម្ងាត់ថ្មី៖ | New Password: | portal |
| ⏳ à relire | ពាក្យសម្ងាត់៖ | Password: | portal |
| ⏳ à relire | បិទវគ្គទាំងអស់ | Revoke All Sessions | portal |
| ⏳ à relire | រក្សាទុកអាសយដ្ឋាន | Save Address | portal |
| ⏳ à relire | ផ្ញើសារ | Send message | portal |
| ⏳ à relire | រំលងទៅមាតិកា | Skip to Content | portal |
| ⏳ à relire | ផ្លូវ និងលេខផ្ទះ | Street and Number | portal |
| ⏳ à relire | បង្ហាញ ឬលាក់តម្រង | Toggle filters | portal |
| ⏳ à relire | បញ្ជាក់ពាក្យសម្ងាត់ថ្មី៖ | Verify New Password: | portal |
| ⏳ à relire | អ្នកទំនាក់ទំនងរបស់លោកអ្នក | Your contact | portal, sale |
| ⏳ à relire | ឈ្មោះរបស់លោកអ្នក | Your name | portal |
| ⏳ à relire | សួស្តី, ការទូទាត់ដែលមានឯកសារយោង SOOO49 ចំនួនទឹកប្រាក់ $ 10.00 សម្រាប់ការបញ្ជាទិញរបស់លោកអ្នក S00049 កំពុងរង់ចាំ។ ការបញ្ជាទិញរបស់លោកអ្នកនឹងត្រូវបញ្ជាក់ នៅពេលការទូទាត់ត្រូវបានបញ្ជាក់។ នៅពេលបញ្ជាក់រួច $ 10.00 នឹងនៅសល់ត្រូវបង់។ ត្រូវបានបញ្ជាក់ហើយ។ $ 10.00 នៅសល់ត្រូវបង់។ សូមអរគុណចំពោះការទុកចិត្តរបស់លោកអ្នក! ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ -- Mitchell Admin | Hello, A payment with reference SOOO49 amounting $ 10.00 for your order S00049 is pending. Your order will be confirmed once the payment is confirmed. Once confirmed, $ 10.00 will remain to be paid. has been confirmed. $ 10.00 remains to be paid. Thank you for your trust! Do not hesitate to contact us if you have any questions. -- Mitchell Admin | sale |
| ⏳ à relire | សួស្តី, ការបញ្ជាទិញរបស់លោកអ្នក S00049 ចំនួនទឹកប្រាក់ $ 10.00 ត្រូវបានបញ្ជាក់ហើយ។ សូមអរគុណចំពោះការទុកចិត្តរបស់លោកអ្នក! កំពុងរង់ចាំ។ វានឹងត្រូវបញ្ជាក់ នៅពេលទទួលបានការទូទាត់។ ឯកសារយោងការទូទាត់របស់លោកអ្នកគឺ . នេះជាឯកសារបន្ថែមមួយចំនួនដែលលោកអ្នកប្រហែលជាចាប់អារម្មណ៍៖ នេះជាឯកសារបន្ថែមដែលលោកអ្នកប្រហែលជាចាប់អារម្មណ៍៖ ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ -- Mitchell Admin ផលិតផល បរិមាណ មិនរួមពន្ធ រួមពន្ធ Taking care of Trees Course Taking care of Trees Course \tTaking care of Trees Course 1 $ 10.00 $ 10.00 សរុបរង៖ $ 10.00 ការដឹកជញ្ជូន៖ $ 0.00 ចំនួនមិនរួមពន្ធ៖ $ 10.00 ចំនួនមិនរួមពន្ធ៖ $ 10.00 ពន្ធ៖ $ 0.00 សរុប៖ $ 10.00 ចេញវិក្កយបត្រជូន៖ 1201 S Figueroa St Los Angeles California 90015 សហរដ្ឋអាមេរិក វិធីទូទាត់៖ ( $ 10.00 ) ដឹកជញ្ជូនទៅ៖ 1201 S Figueroa St Los Angeles California 90015 សហរដ្ឋអាមេរិក វិធីដឹកជញ្ជូន៖ (ឥតគិតថ្លៃ) ( $ 10.00 ) ការពិពណ៌នាការដឹកជញ្ជូន៖ | Hello, Your order S00049 amounting in $ 10.00 has been confirmed. Thank you for your trust! is pending. It will be confirmed when the payment is received. Your payment reference is . Here are some additional documents that may interest you: Here is an additional document that may interest you: Do not hesitate to contact us if you have any questions. -- Mitchell Admin Products Quantity Tax Excl. Tax Incl. Taking care of Trees Course Taking care of Trees Course \tTaking care of Trees Course 1 $ 10.00 $ 10.00 Subtotal: $ 10.00 Delivery: $ 0.00 Untaxed Amount: $ 10.00 Untaxed Amount: $ 10.00 Taxes: $ 0.00 Total: $ 10.00 Bill to: 1201 S Figueroa St Los Angeles California 90015 United States Payment Method: ( $ 10.00 ) Ship to: 1201 S Figueroa St Los Angeles California 90015 United States Shipping Method: (Free) ( $ 10.00 ) Shipping Description: | sale |
| ⏳ à relire | សួស្តី, សម្រង់តម្លៃរបស់លោកអ្នក (ឯកសារយោង៖ S00052 ) ចំនួនទឹកប្រាក់ $ 10.00 រួចរាល់សម្រាប់ការពិនិត្យ។ ការបញ្ជាទិញរបស់លោកអ្នក (ឯកសារយោង៖ S00052 ) ចំនួនទឹកប្រាក់ $ 10.00 រួចរាល់សម្រាប់ការពិនិត្យ។ នេះជាឯកសារបន្ថែមមួយចំនួនដែលលោកអ្នកប្រហែលជាចាប់អារម្មណ៍៖ នេះជាឯកសារបន្ថែមដែលលោកអ្នកប្រហែលជាចាប់អារម្មណ៍៖ ប្រសិនបើមានសំណួរ សូមកុំស្ទាក់ស្ទើរក្នុងការទាក់ទងមកយើង។ -- Mitchell Admin | Hello, Your quotation (with reference: S00052 ) amounting in $ 10.00 is ready for review. Your order (with reference: S00052 ) amounting in $ 10.00 is ready for review. Here are some additional documents that may interest you: Here is an additional document that may interest you: Do not hesitate to contact us if you have any questions. -- Mitchell Admin | sale |
| ⏳ à relire | អាសយដ្ឋានចេញវិក្កយបត្រ និងដឹកជញ្ជូន | Invoicing and Shipping Address | sale |
| ⏳ à relire | ឯកសារយោងរបស់លោកអ្នក | Your Reference | sale |
| ⏳ à relire | យល់ព្រម និងចុះហត្ថលេខា | Accept & Sign | portal, sale |
| ⏳ à relire | ចំនួនទឹកប្រាក់៖ | Amount: | sale |
| ⏳ à relire | ដោយចុះហត្ថលេខា លោកអ្នកបញ្ជាក់ការយល់ព្រមក្នុងនាម | By signing, you confirm acceptance on behalf of | sale |
| ⏳ à relire | ចម្លង | Copy | auth_totp_portal, sale |
| ⏳ à relire | ឯកសារណែនាំ | Documentation | sale |
| ⏳ à relire | កាលបរិច្ឆេទផុតកំណត់៖ | Expiration Date: | sale |
| ⏳ à relire | តាមដាន មើល ឬបង់ការបញ្ជាទិញរបស់លោកអ្នក | Follow, view or pay your orders | sale |
| ⏳ à relire | សម្រង់តម្លៃ | Quotation | sale |
| ⏳ à relire | សម្រង់តម្លៃ | Quotations | sale |
| ⏳ à relire | បដិសេធសម្រង់តម្លៃនេះ | Reject This Quotation | sale |
| ⏳ à relire | ព័ត៌មានការលក់ | Sale Information | sale |
| ⏳ à relire | ការបញ្ជាទិញ | Sales Orders | sale |
| ⏳ à relire | បច្ចុប្បន្នមិនមានសម្រង់តម្លៃសម្រាប់គណនីរបស់លោកអ្នកទេ។ | There are currently no quotations for your account. | sale |
| ⏳ à relire | បញ្ជាក់ការបញ្ជាទិញ | Validate Order | sale |
| ⏳ à relire | ការបញ្ជាទិញរបស់លោកអ្នក | Your Orders | sale |
| ⏳ à relire | ឯកសារយោងរបស់លោកអ្នក៖ | Your Reference: | sale |
| ⏳ à relire | មតិរបស់លោកអ្នក... | Your feedback... | sale |
| ⏳ à relire | សម្រាប់ | for the | sale |
| ⏳ à relire | សម្រង់តម្លៃនេះ។ | quote. | sale |
| ⏳ à relire | {{ object.company_id.name }} {{ (object.get_portal_last_transaction().state == 'pending') and 'Pending Order' or 'Order' }} (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} {{ (object.get_portal_last_transaction().state == 'pending') and 'Pending Order' or 'Order' }} (Ref {{ object.name or 'n/a' }}) | sale |
| ⏳ à relire | {{ object.company_id.name }} {{ object.state in ('draft', 'sent') and 'Quotation' or 'Order' }} (យោង {{ object.name or 'n/a' }}) | {{ object.company_id.name }} {{ object.state in ('draft', 'sent') and 'Quotation' or 'Order' }} (Ref {{ object.name or 'n/a' }}) | sale |
| ⏳ à relire | សំណើចុះហត្ថលេខា | Signature Requests | sign_oca |
| ⏳ à relire | មើល ឬចុះហត្ថលេខាលើឯកសារ | View, or sign documents | sign_oca |
| ⏳ à relire | - ឬ - | - or - | web |
| ⏳ à relire | បញ្ចូលអ៊ីមែលរបស់លោកអ្នក | Enter your email | web |
| ⏳ à relire | ចូលគណនី | Log in | auth_totp, web |
| ⏳ à relire | វិក្កយបត្រព្រាង | Draft Invoice | account |
| ⏳ à relire | បានបង់ | Paid | account, account_payment, sale |
| ⏳ à relire | បានកែបញ្ច្រាស | Reversed | account, sale |
| ⏳ à relire | កំពុងដំណើរការការទូទាត់ | Processing Payment | account, account_payment |
| ⏳ à relire | បានបង់រួច៖ | Already Paid: | account |
| ⏳ à relire | បានផ្អាក | Blocked | account |
| ⏳ à relire | លិខិតឥណទានអតិថិជន | Customer Credit Note | account |
| ⏳ à relire | វិក្កយបត្រអតិថិជន | Customer Invoice | account |
| ⏳ à relire | ព្រាង | Draft | account |
| ⏳ à relire | កំពុងទូទាត់ | In Payment | account |
| ⏳ à relire | សញ្ញាសម្គាល់មិនត្រឹមត្រូវ | Invalid token | account |
| ⏳ à relire | វិក្កយបត្រ | Invoices | account |
| ⏳ à relire | ប្រតិបត្តិការគណនេយ្យ | Journal Entry | account |
| ⏳ à relire | នៅសល់ត្រូវបង់៖ | Left to Pay: | account |
| ⏳ à relire | ការបង់រំលស់បន្ទាប់ | Next Installment | account |
| ⏳ à relire | មិនទាន់បង់ | Not Paid | account |
| ⏳ à relire | ហួសកំណត់ | Overdue | account |
| ⏳ à relire | វិក្កយបត្រហួសកំណត់ | Overdue invoices | account |
| ⏳ à relire | បានបង់មួយផ្នែក | Partially Paid | account |
| ⏳ à relire | បានចុះបញ្ជី | Posted | account |
| ⏳ à relire | បង្កាន់ដៃទិញ | Purchase Receipt | account |
| ⏳ à relire | បង្កាន់ដៃលក់ | Sales Receipt | account |
| ⏳ à relire | បច្ចុប្បន្នមិនមានវិក្កយបត្រ ឬការទូទាត់សម្រាប់គណនីរបស់លោកអ្នកទេ។ | There are currently no invoices and payments for your account. | account |
| ⏳ à relire | មានកំហុសកើតឡើងពេលដំណើរការទំព័រនេះ។ | There was an error processing this page. | account |
| ⏳ à relire | វិក្កយបត្រអ្នកផ្គត់ផ្គង់ | Vendor Bill | account |
| ⏳ à relire | លិខិតឥណទានអ្នកផ្គត់ផ្គង់ | Vendor Credit Note | account |
| ⏳ à relire | បិទ | close | account, sale |
| ⏳ à relire | ហួសកំណត់ %s ថ្ងៃ | %s day(s) overdue | account_payment |
| ⏳ à relire | បានអនុញ្ញាត | Authorized | account_payment, sale |
| ⏳ à relire | កំពុងរង់ចាំ | Pending | account_payment |
| ⏳ à relire | ចំនួនពេញ | Full Amount | account_payment |
| ⏳ à relire | ការបង់រំលស់ | Installment | account_payment |
| ⏳ à relire | មានការទូទាត់មួយរួចហើយលើវិក្កយបត្រនេះ សូមប្រយ័ត្នកុំបង់ពីរដង។ | A payment has already been made on this invoice, please make sure to not pay twice. | account_payment |
| ⏳ à relire | រួចរាល់ ការទូទាត់តាមអនឡាញរបស់លោកអ្នកបានជោគជ័យ។ សូមអរគុណសម្រាប់ការបញ្ជាទិញ។ | Done, your online payment has been successfully processed. Thank you for your order. | account_payment |
| ⏳ à relire | បញ្ចុះតម្លៃសម្រាប់ការបង់ប្រាក់មុនកំណត់ ចំនួន | Early Payment Discount of | account_payment |
| ⏳ à relire | បង់វិក្កយបត្រ | Pay Invoice | account_payment |
| ⏳ à relire | បង់វិក្កយបត្រហួសកំណត់ | Pay overdue | account_payment |
| ⏳ à relire | សូមចូលគណនី ដើម្បីបង់វិក្កយបត្រហួសកំណត់របស់លោកអ្នក | Please log in to pay your overdue invoices | account_payment |
| ⏳ à relire | សញ្ញាសម្គាល់ចូលប្រើមិនត្រឹមត្រូវ។ | The access token is invalid. | account_payment, sale |
| ⏳ à relire | ផុតកំណត់ក្នុង %s ថ្ងៃ | due in %s day(s) | account_payment |
| ⏳ à relire | ផុតកំណត់ថ្ងៃនេះ | due today | account_payment |
| ⏳ à relire | ត្រូវបានអនុវត្តហើយ។ | has been applied. | account_payment |
| ⏳ à relire | ហួសកំណត់ | overdue | account_payment |
| ⏳ à relire | បោះបង់ | Cancel | auth_passkey, auth_totp, mail, portal, sale, web |
| ⏳ à relire | បង្កើត | Create | auth_passkey, auth_passkey_portal |
| ⏳ à relire | រក្សាទុក | Save | auth_passkey |
| ⏳ à relire | បង្កើត Passkey | Create Passkey | auth_passkey_portal |
| ⏳ à relire | បានបង្កើត | Created | auth_passkey_portal |
| ⏳ à relire | ដាក់ឈ្មោះកូនសោរបស់លោកអ្នក | Name your key | auth_passkey_portal, portal |
| ⏳ à relire | ប្តូរឈ្មោះ | Rename | auth_passkey_portal |
| ⏳ à relire | ប្តូរឈ្មោះកូនសោរបស់លោកអ្នក | Rename your key | auth_passkey_portal |
| ⏳ à relire | , មានការស្នើសុំកំណត់ពាក្យសម្ងាត់ឡើងវិញសម្រាប់គណនីដែលភ្ជាប់នឹងអ៊ីមែលនេះ។ លោកអ្នកអាចប្តូរពាក្យសម្ងាត់ដោយចុចតំណខាងក្រោម ដែលមានសុពលភាពក្នុងរយៈពេល | , A password reset was requested for the account linked to this email. You may change your password by following this link which will remain valid during | auth_signup |
| ⏳ à relire | គណនីរបស់លោកអ្នក | Your Account | auth_signup |
| ⏳ à relire | មានគណនីរួចហើយ? | Already have an account? | auth_signup |
| ⏳ à relire | មានអ្នកប្រើម្នាក់ទៀតបានចុះឈ្មោះដោយប្រើអាសយដ្ឋានអ៊ីមែលនេះរួចហើយ។ | Another user is already registered using this email address. | auth_signup |
| ⏳ à relire | ប្តូរពាក្យសម្ងាត់ | Change password | auth_signup |
| ⏳ à relire | បញ្ជាក់ពាក្យសម្ងាត់ | Confirm Password | auth_signup, portal |
| ⏳ à relire | មិនអាចបង្កើតគណនីថ្មីបានទេ។ | Could not create a new account. | auth_signup |
| ⏳ à relire | មិនអាចកំណត់ពាក្យសម្ងាត់របស់លោកអ្នកឡើងវិញបានទេ | Could not reset your password | auth_signup |
| ⏳ à relire | ជូនចំពោះ | Dear | auth_signup, portal |
| ⏳ à relire | មិនទាន់មានគណនី? | Don't have an account? | auth_signup |
| ⏳ à relire | ប្រសិនបើលោកអ្នកមិនបានស្នើសុំទេ សូមមិនអើពើនឹងអ៊ីមែលនេះ។ សូមអរគុណ, | If you do not expect this, you can safely ignore this email. Thanks, | auth_signup |
| ⏳ à relire | សញ្ញាសម្គាល់ចុះឈ្មោះមិនត្រឹមត្រូវ | Invalid signup token | auth_signup |
| ⏳ à relire | មិនបានបញ្ចូលឈ្មោះចូលទេ។ | No login provided. | auth_signup |
| ⏳ à relire | ការណែនាំអំពីការកំណត់ពាក្យសម្ងាត់ឡើងវិញ ត្រូវបានផ្ញើទៅអ៊ីមែលរបស់លោកអ្នកហើយ។ | Password reset instructions sent to your email address. | auth_signup |
| ⏳ à relire | ពាក្យសម្ងាត់មិនដូចគ្នាទេ សូមវាយបញ្ចូលម្តងទៀត។ | Passwords do not match; please retype them. | auth_signup |
| ⏳ à relire | ការចុះឈ្មោះបានជោគជ័យ។ | Registration successful. | auth_signup |
| ⏳ à relire | ចុះឈ្មោះ | Sign Up | auth_signup |
| ⏳ à relire | ចុះឈ្មោះ | Sign up | auth_signup |
| ⏳ à relire | ទម្រង់បែបបទមិនបានបំពេញត្រឹមត្រូវទេ។ | The form was not properly filled in. | auth_signup |
| ⏳ à relire | ពាក្យសម្ងាត់របស់លោកអ្នកត្រូវបានកំណត់ឡើងវិញដោយជោគជ័យ។ | Your password has been reset successfully. | auth_signup |
| ⏳ à relire | ម៉ោង៖ | hours: | auth_signup |
| ⏳ à relire | %(browser)s លើ %(platform)s | %(browser)s on %(platform)s | auth_totp |
| ⏳ à relire | បញ្ចូលកូនសោនេះទៅក្នុងកម្មវិធី Authenticator របស់លោកអ្នក | Add this key in your Authenticator app | auth_totp |
| ⏳ à relire | កូដផ្ទៀងផ្ទាត់ | Authentication Code | auth_totp |
| ⏳ à relire | ស្កេនមិនបាន? | Cannot scan it? | auth_totp |
| ⏳ à relire | កុំសួរម្តងទៀតលើឧបករណ៍នេះ | Don't ask again on this device | auth_totp |
| ⏳ à relire | បើកការផ្ទៀងផ្ទាត់ពីរជំហាន | Enable Two-Factor Authentication | auth_totp |
| ⏳ à relire | ទម្រង់កូដផ្ទៀងផ្ទាត់មិនត្រឹមត្រូវ។ | Invalid authentication code format. | auth_totp |
| ⏳ à relire | ស្វែងយល់បន្ថែម | Learn More | auth_totp, auth_totp_mail |
| ⏳ à relire | ស្កេនបាកូដនេះដោយកម្មវិធី Authenticator របស់លោកអ្នក | Scan this barcode in your Authenticator app | auth_totp |
| ⏳ à relire | ដើម្បីចូលគណនី សូមបញ្ចូលខាងក្រោមនូវកូដផ្ទៀងផ្ទាត់ 6 ខ្ទង់ ដែលកម្មវិធី Authenticator របស់លោកអ្នកផ្តល់ឱ្យ។ | To login, enter below the six-digit authentication code provided by your Authenticator app. | auth_totp |
| ⏳ à relire | ការផ្ទៀងផ្ទាត់ពីរជំហាន | Two-factor Authentication | auth_totp |
| ⏳ à relire | កូដផ្ទៀងផ្ទាត់ | Verification code | auth_totp |
| ⏳ à relire | បញ្ចូលកូដដែលកម្មវិធីរបស់លោកអ្នកផ្តល់ឱ្យ | Write the code given by your app | auth_totp |
| ⏳ à relire | ដើម្បីចូលគណនី សូមបញ្ចូលខាងក្រោមនូវកូដផ្ទៀងផ្ទាត់ 6 ខ្ទង់ ដែលទើបផ្ញើតាមអ៊ីមែលទៅ | To login, enter below the six-digit authentication code just sent via email to | auth_totp_mail |
| ⏳ à relire | ផ្ញើអ៊ីមែលម្តងទៀត | Re-send email | auth_totp_mail |
| ⏳ à relire | យើងសូមណែនាំឱ្យបើកការផ្ទៀងផ្ទាត់ពីរជំហានដោយប្រើកម្មវិធី Authenticator ដើម្បីជួយការពារគណនីរបស់លោកអ្នក។ | We strongly recommend enabling the two-factor authentication using an authenticator app to help secure your account. | auth_totp_mail |
| ⏳ à relire | (បិទការផ្ទៀងផ្ទាត់ពីរជំហាន) | (Disable two-factor authentication) | auth_totp_portal |
| ⏳ à relire | បានបើកការផ្ទៀងផ្ទាត់ពីរជំហាន | Two-factor authentication enabled | auth_totp_portal |
| ⏳ à relire | បន្ថែមនៅថ្ងៃ | Added On | auth_totp_portal, portal |
| ⏳ à relire | ឧបករណ៍ដែលទុកចិត្ត | Trusted Device | auth_totp_portal |
| ⏳ à relire | បើកដំណើរការ | Activate | auth_totp_portal |
| ⏳ à relire | បានចម្លង! | Copied! | auth_totp_portal |
| ⏳ à relire | ប្រតិបត្តិការបរាជ័យដោយមិនដឹងមូលហេតុ។ | Operation failed for unknown reason. | auth_totp_portal |
| ⏳ à relire | ដកហូតទាំងអស់ | Revoke All | auth_totp_portal |
| ⏳ à relire | លក្ខខណ្ឌទូទាត់ | Payment Terms | contract |
| ⏳ à relire | ថ្ងៃ | Day(s) | contract |
| ⏳ à relire | ថ្ងៃចុងខែ | Month(s) last day | contract |
| ⏳ à relire | បង់ក្រោយ | Post-paid | contract |
| ⏳ à relire | បង់មុន | Pre-paid | contract |
| ⏳ à relire | ត្រីមាស | Quarter(s) | contract |
| ⏳ à relire | ឆមាស | Semester(s) | contract |
| ⏳ à relire | បច្ចុប្បន្នមិនមានកិច្ចសន្យាសម្រាប់គណនីរបស់លោកអ្នកទេ។ | There are currently no contracts for your account. | contract |
| ⏳ à relire | សប្តាហ៍ | Week(s) | contract |
| ⏳ à relire | ឆ្នាំ | Year(s) | contract |
| ⏳ à relire | ខ្ពស់ | High | fieldservice |
| ⏳ à relire | ទាប | Low | fieldservice |
| ⏳ à relire | ធម្មតា | Normal | fieldservice |
| ⏳ à relire | បន្ទាន់ | Urgent | fieldservice |
| ⏳ à relire | ថ្មីបំផុត | Newest | fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | ស្វែងរកក្នុងទាំងអស់ | Search in All | fieldservice_portal, helpdesk_mgmt |
| ⏳ à relire | ស្វែងរកក្នុងការពិពណ៌នា | Search in Description | fieldservice_portal |
| ⏳ à relire | ស្វែងរកក្នុងលេខទីតាំង | Search in Location Numbers | fieldservice_portal |
| ⏳ à relire | ស្វែងរកក្នុងលេខការចុះជួសជុល | Search in WO Number | fieldservice_portal |
| ⏳ à relire | ការចុះជួសជុលសម្រាប់ | Work Orders for | fieldservice_portal |
| ⏳ à relire | សំណើជំនួយក្នុងប្រភេទ៖ | Tickets in category: | helpdesk_mgmt |
| ⏳ à relire | សំណើជំនួយក្នុងដំណាក់កាល៖ | Tickets in stage: | helpdesk_mgmt |
| ⏳ à relire | កាលបរិច្ឆេទបិទ៖ | Closed Date: | helpdesk_mgmt |
| ⏳ à relire | ឯកសារភ្ជាប់ | Attachments | helpdesk_mgmt |
| ⏳ à relire | រកមិនឃើញសំណើជំនួយទេ។ | No tickets found. | helpdesk_mgmt |
| ⏳ à relire | ស្វែងរកក្នុងលេខ | Search in Number | helpdesk_mgmt |
| ⏳ à relire | ស្វែងរកក្នុងចំណងជើង | Search in Title | helpdesk_mgmt |
| ⏳ à relire | ក្រុម | Team | helpdesk_mgmt |
| ⏳ à relire | ឯកសារដែលបានជ្រើសរើស (%sB) ធំជាងទំហំអតិបរមាដែលអនុញ្ញាត (%sB)។ | The selected file (%sB) is over the maximum allowed file size (%sB). | helpdesk_mgmt |
| ⏳ à relire | បុគ្គលិក | Employee | helpdesk_mgmt_timesheet |
| ⏳ à relire | ពេលវេលាដែលបានចំណាយ | Spent Time | helpdesk_mgmt_timesheet |
| ⏳ à relire | ពេលវេលាដែលបានចំណាយ | Time Spent | helpdesk_mgmt_timesheet |
| ⏳ à relire | 403៖ មិនអនុញ្ញាត | 403: Forbidden | http_routing |
| ⏳ à relire | សូមកុំបារម្ភ។ ប្រសិនបើលោកអ្នកគិតថាជាកំហុសរបស់យើង សូមផ្ញើសារមកយើងតាម | Don't panic. If you think it's our mistake, please send us a message on | http_routing |
| ⏳ à relire | សារកំហុស៖ | Error message: | http_routing |
| ⏳ à relire | កំហុស 404 | Error 404 | http_routing |
| ⏳ à relire | ប្រហែលជាលោកអ្នកកំពុងរក ទំព័រដែលគេចូលមើលច្រើនទាំងនេះ? | Maybe you were looking for one of these popular pages? | http_routing |
| ⏳ à relire | លោកអ្នកមិនមានសិទ្ធិចូលមើលទំព័រនេះទេ។ | The page you were looking for could not be authorized. | http_routing |
| ⏳ à relire | យើងរកមិនឃើញទំព័រដែលលោកអ្នកកំពុងរកទេ! | We couldn't find the page you're looking for! | http_routing |
| ⏳ à relire | ទំព័រនេះ | this page | http_routing |
| ⏳ à relire | %(file1)s និងឯកសារភ្ជាប់ %(count)s ផ្សេងទៀត | %(file1)s and %(count)s other attachments | mail |
| ⏳ à relire | %(file1)s និង %(file2)s | %(file1)s and %(file2)s | mail |
| ⏳ à relire | (បានកែប្រែ) | (edited) | mail |
| ⏳ à relire | បន្ថែមរូបអារម្មណ៍ | Add Emojis | mail |
| ⏳ à relire | បន្ថែមប្រតិកម្ម | Add a Reaction | mail |
| ⏳ à relire | មានកំហុសកើតឡើងពេលទាញយកសារ។ | An error occurred while fetching messages. | mail |
| ⏳ à relire | ភ្ជាប់ឯកសារ | Attach Files | mail |
| ⏳ à relire | ភ្ជាប់ឯកសារ | Attach files | mail |
| ⏳ à relire | រូបតំណាង | Avatar | mail, portal |
| ⏳ à relire | រូបតំណាងអ្នកប្រើ | Avatar of user | mail |
| ⏳ à relire | ចុចទីនេះដើម្បីព្យាយាមម្តងទៀត | Click here to retry | mail |
| ⏳ à relire | ការបញ្ជាក់ | Confirmation | mail, web |
| ⏳ à relire | ចម្លងតំណ | Copy Link | mail |
| ⏳ à relire | ជូនចំពោះអ្នកផ្ញើ, | Dear Sender, | mail |
| ⏳ à relire | លុប | Delete | mail, portal |
| ⏳ à relire | តើលោកអ្នកពិតជាចង់លុប "%s" មែនទេ? | Do you really want to delete "%s"? | mail |
| ⏳ à relire | ទាញយកឯកសារ | Download Files | mail |
| ⏳ à relire | កែប្រែ | Edit | mail |
| ⏳ à relire | រូបអារម្មណ៍ | Emoji | mail |
| ⏳ à relire | ពង្រីក | Expand | mail, web |
| ⏳ à relire | ផ្ញើសារមិនបានទេ។ ចុចដើម្បីព្យាយាមម្តងទៀត | Failed to post the message. Click to retry | mail |
| ⏳ à relire | ឯកសារធំពេក | File too large | mail |
| ⏳ à relire | ដោយក្តីគោរព | Kind Regards | mail |
| ⏳ à relire | បង្ហាញបន្ថែម | Load More | mail |
| ⏳ à relire | កំពុងផ្ទុក… | Loading… | mail |
| ⏳ à relire | សារ | Message | mail |
| ⏳ à relire | បានចម្លងតំណសារ! | Message Link Copied! | mail |
| ⏳ à relire | ទេ | No | mail |
| ⏳ à relire | កំណត់ចំណាំ | Note | mail |
| ⏳ à relire | បើកតំណ | Open Link | mail |
| ⏳ à relire | សូមរង់ចាំ ឯកសារកំពុងផ្ទុកឡើង។ | Please wait while the file is uploading. | mail |
| ⏳ à relire | មើលជាមុន | Preview | mail |
| ⏳ à relire | ដកចេញ | Remove | mail |
| ⏳ à relire | ឆ្លើយតប | Reply | mail |
| ⏳ à relire | កំពុងឆ្លើយតបទៅ | Replying to | mail |
| ⏳ à relire | ផ្ញើ | Send | account, mail, portal, sale |
| ⏳ à relire | កំហុសម៉ាស៊ីនមេ | Server error | mail |
| ⏳ à relire | ប្រធានបទ៖ | Subject: | mail |
| ⏳ à relire | មិនទាន់មានសារនៅឡើយទេ។ | The conversation is empty. | mail |
| ⏳ à relire | សារខាងក្រោមមិនអាចទទួលបានដោយអាសយដ្ឋាន | The message below could not be accepted by the address | mail |
| ⏳ à relire | សារនេះត្រូវបានលុបចេញហើយ | This message has been removed | mail |
| ⏳ à relire | ថ្ងៃនេះ | Today | mail |
| ⏳ à relire | ឈប់តាមដាន | Unfollow | mail |
| ⏳ à relire | បានផ្ទុកឡើង | Uploaded | mail |
| ⏳ à relire | កំពុងផ្ទុកឡើង | Uploading | mail |
| ⏳ à relire | មើលប្រតិកម្ម | View Reactions | mail |
| ⏳ à relire | បាទ/ចាស | Yes | mail |
| ⏳ à relire | ម្សិលមិញ ម៉ោង %(time)s | Yesterday at %(time)s | mail |
| ⏳ à relire | ដោយសារលោកអ្នកបានទាក់ទងច្រើនដងពេកក្នុងរយៈពេលប៉ុន្មាននាទីចុងក្រោយនេះ។ សូមព្យាយាមម្តងទៀតនៅពេលក្រោយ។ | because you have contacted it too many times in the last few minutes. Please try again later. | mail |
| ⏳ à relire | ឬចុច %(send_keybind)s | or press %(send_keybind)s | mail |
| ⏳ à relire | " ដើម្បីបញ្ជាក់សកម្មភាពនេះ។ | " to validate your action. | portal |
| ⏳ à relire | ហួសកំណត់ %s ថ្ងៃ | %s days overdue | portal |
| ⏳ à relire | ២. បញ្ជាក់ថាលោកអ្នកចង់លុបគណនី ដោយវាយបញ្ចូលឈ្មោះចូលរបស់លោកអ្នក ( | 2. Confirm you want to delete your account by copying down your login ( | portal |
| ⏳ à relire | បន្ថែមអាសយដ្ឋាន | Add Address | portal |
| ⏳ à relire | មិនអនុញ្ញាតឱ្យប្តូរលេខអត្តសញ្ញាណកម្ម អតប ទេ នៅពេលមានឯកសារចេញសម្រាប់គណនីរបស់លោកអ្នករួចហើយ។ សូមទាក់ទងមកយើងផ្ទាល់សម្រាប់ប្រតិបត្តិការនេះ។ | Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation. | portal |
| ⏳ à relire | លេខអត្តសញ្ញាណកម្ម អតប អាចកែប្រែបានតែលើគណនីក្រុមហ៊ុនប៉ុណ្ណោះ។ | The VAT number can only be updated on the company account. | portal |
| ⏳ à relire | មិនអនុញ្ញាតឱ្យប្តូរប្រទេសទេ នៅពេលមានឯកសារចេញសម្រាប់គណនីរបស់លោកអ្នករួចហើយ។ សូមទាក់ទងមកយើងផ្ទាល់សម្រាប់ប្រតិបត្តិការនេះ។ | Changing country is not allowed once document(s) have been issued for your account. Please contact us directly for this operation. | portal |
| ⏳ à relire | គណនីត្រូវបានលុបហើយ! | Account deleted! | portal |
| ⏳ à relire | បន្ថែមអាសយដ្ឋាន | Add an address | portal |
| ⏳ à relire | បន្ថែមឯកសារភ្ជាប់ | Add attachment | portal |
| ⏳ à relire | អាសយដ្ឋានចេញវិក្កយបត្រ | Billing Address | portal |
| ⏳ à relire | អាសយដ្ឋានចេញវិក្កយបត្រ | Billing address | portal |
| ⏳ à relire | មិនអនុញ្ញាតឱ្យប្តូរប្រទេសទេ នៅពេលមានឯកសារចេញសម្រាប់គណនីរបស់លោកអ្នករួចហើយ។ សូមទាក់ទងមកយើងផ្ទាល់សម្រាប់ប្រតិបត្តិការនេះ។ | Changing your country is not allowed once document(s) have been issued for your account. Please contact us directly for this operation. | portal |
| ⏳ à relire | ការផ្ទៀងផ្ទាត់បរាជ័យ | Check failed | portal |
| ⏳ à relire | ចុចទីនេះដើម្បីមើលឯកសាររបស់លោកអ្នក។ | Click here to see your document. | portal |
| ⏳ à relire | ឈ្មោះក្រុមហ៊ុន | Company Name | portal |
| ⏳ à relire | បញ្ជាក់ | Confirm | portal |
| ⏳ à relire | ព័ត៌មានទំនាក់ទំនង | Contact Details | portal |
| ⏳ à relire | មិនអាចរក្សាទុកឯកសារ %s បានទេ | Could not save file %s | portal |
| ⏳ à relire | អាសយដ្ឋានដឹកជញ្ជូន | Delivery Address | portal |
| ⏳ à relire | អាសយដ្ឋានដឹកជញ្ជូន | Delivery address | portal |
| ⏳ à relire | ផុតកំណត់ក្នុង %s ថ្ងៃ | Due in %s days | portal |
| ⏳ à relire | ផុតកំណត់ថ្ងៃនេះ | Due today | portal |
| ⏳ à relire | កែប្រែអាសយដ្ឋាននេះ | Edit this address | portal |
| ⏳ à relire | ភ្លេចពាក្យសម្ងាត់? | Forgot password? | portal |
| ⏳ à relire | ប្រសិនបើចង់កែប្រែ សូមធ្វើបច្ចុប្បន្នភាព | If you want to modify it, update | portal |
| ⏳ à relire | អ៊ីមែលមិនត្រឹមត្រូវ! សូមបញ្ចូលអាសយដ្ឋានអ៊ីមែលដែលត្រឹមត្រូវ។ | Invalid Email! Please enter a valid email address. | portal |
| ⏳ à relire | ផ្តល់មតិ | Leave a comment | portal |
| ⏳ à relire | អាសយដ្ឋានចម្បង | Main Address | portal |
| ⏳ à relire | អាសយដ្ឋានរបស់ខ្ញុំ | My addresses | portal |
| ⏳ à relire | បន្ទាប់ | Next | portal |
| ⏳ à relire | ស្លាកសញ្ញា Odoo | Odoo Logo | portal |
| ⏳ à relire | មានបញ្ហាកើតឡើង។ សូមផ្ទុកទំព័រឡើងវិញ ហើយចូលគណនីម្តងទៀត។ | Oops! Something went wrong. Try to reload the page and log in. | portal |
| ⏳ à relire | ពាក្យសម្ងាត់ត្រូវបានប្តូរហើយ! | Password Updated! | portal |
| ⏳ à relire | ទូរស័ព្ទ | Phone | portal |
| ⏳ à relire | សូមបញ្ចូលពាក្យសម្ងាត់ ដើម្បីបញ្ជាក់ថាលោកអ្នកជាម្ចាស់គណនីនេះ | Please enter your password to confirm you own this account | portal |
| ⏳ à relire | មុន | Previous | portal |
| ⏳ à relire | ដាក់អ៊ីមែល និងលេខទូរស័ព្ទរបស់ខ្ញុំក្នុងបញ្ជីហាមទាក់ទង ដើម្បីកុំឱ្យមានការទាក់ទងមកខ្ញុំទៀត | Put my email and phone in a block list to make sure I'm never contacted again | portal |
| ⏳ à relire | លុបអាសយដ្ឋាននេះ | Remove this address | portal |
| ⏳ à relire | ដូចអាសយដ្ឋានដឹកជញ្ជូន | Same as delivery address | portal |
| ⏳ à relire | សុវត្ថិភាព | Security | portal |
| ⏳ à relire | ការត្រួតពិនិត្យសុវត្ថិភាព | Security Control | portal |
| ⏳ à relire | ចូលគណនី | Sign in | portal |
| ⏳ à relire | ត្រូវបំពេញព័ត៌មានខ្លះ។ សូមសរសេរសារ ឬភ្ជាប់ឯកសារ | Some fields are required. Please make sure to write a message or attach a document | portal |
| ⏳ à relire | ព័ត៌មានចាំបាច់ខ្លះមិនទាន់បានបំពេញ។ | Some required fields are empty. | portal |
| ⏳ à relire | ខេត្ត / រដ្ឋ | State / Province | portal |
| ⏳ à relire | សូមអរគុណ! | Thank You! | portal, sale |
| ⏳ à relire | %(field_name)s ត្រូវបានគ្រប់គ្រងលើគណនីក្រុមហ៊ុនរបស់លោកអ្នក។ | The %(field_name)s is managed on your company account. | portal |
| ⏳ à relire | %(field_name)s ត្រូវបានគ្រប់គ្រងលើអាសយដ្ឋានចម្បងនៃគណនីរបស់លោកអ្នក។ | The %(field_name)s is managed on your main account address. | portal |
| ⏳ à relire | មិនអាចដកឯកសារភ្ជាប់ %s ចេញបានទេ ព្រោះវាភ្ជាប់ជាមួយសារមួយ។ | The attachment %s cannot be removed because it is linked to a message. | portal |
| ⏳ à relire | ឯកសារភ្ជាប់មិនមានទេ ឬលោកអ្នកគ្មានសិទ្ធិចូលមើលវា។ | The attachment does not exist or you do not have the rights to access it. | portal |
| ⏳ à relire | ឈ្មោះក្រុមហ៊ុន និងលេខអត្តសញ្ញាណកម្ម អតប អាចកែប្រែបានតែលើគណនីចម្បងរបស់លោកអ្នកប៉ុណ្ណោះ។ | The company name and VAT number can only be updated on your main account. | portal |
| ⏳ à relire | ពាក្យសម្ងាត់ថ្មី និងការបញ្ជាក់ត្រូវតែដូចគ្នា។ | The new password and its confirmation must be identical. | portal |
| ⏳ à relire | ពាក្យសម្ងាត់ចាស់ដែលលោកអ្នកបញ្ចូលមិនត្រឹមត្រូវ ពាក្យសម្ងាត់មិនត្រូវបានប្តូរទេ។ | The old password you provided is incorrect, your password was not changed. | portal |
| ⏳ à relire | ឯកសារនេះមិនមានទេ។ | This document does not exist. | portal |
| ⏳ à relire | សរសេរសារ... | Write a message... | portal |
| ⏳ à relire | សរសេរសារ… | Write a message… | portal |
| ⏳ à relire | ពាក្យសម្ងាត់មិនត្រឹមត្រូវ។ | Wrong password. | portal |
| ⏳ à relire | លោកអ្នកមិនអាចលុបអាសយដ្ឋានចម្បងរបស់លោកអ្នកបានទេ | You cannot archive your main address | portal |
| ⏳ à relire | មិនអាចទុកប្រអប់ពាក្យសម្ងាត់ណាមួយឱ្យទទេបានទេ។ | You cannot leave any password empty. | portal |
| ⏳ à relire | លោកអ្នកត្រូវ | You must be | portal |
| ⏳ à relire | លោកអ្នកត្រូវបញ្ចូល " | You should enter " | portal |
| ⏳ à relire | បានអញ្ជើញលោកអ្នកឱ្យចូលមើល | has invited you to access the following | portal |
| ⏳ à relire | ចូលគណនី | logged in | portal |
| ⏳ à relire | ដើម្បីផ្តល់មតិ។ | to post a comment. | portal |
| ⏳ à relire | ព័ត៌មានគណនីរបស់លោកអ្នក | your account details | portal |
| ⏳ à relire | សូមទាក់ទងមកយើង ដើម្បីទទួលបានសម្រង់តម្លៃថ្មី។ | Contact us to get a new quotation. | sale |
| ⏳ à relire | កំពុងរង់ចាំការទូទាត់ | Waiting Payment | sale |
| ⏳ à relire | អត្ថប្រយោជន៍របស់លោកអ្នក | Your advantage | sale |
| ⏳ à relire | ការបញ្ជាទិញលេខ យោង | Sales Order # Ref. | sale |
| ⏳ à relire | ដោយបង់ប្រាក់ | By paying, | sale |
| ⏳ à relire | បញ្ចុះ% | Disc.% | sale |
| ⏳ à relire | សម្រង់តម្លៃនេះផុតកំណត់ហើយ! | This offer expired! | sale |
| ⏳ à relire | សម្រង់តម្លៃនេះត្រូវបានលុបចោលហើយ។ | This quotation has been cancelled. | sale |
| ⏳ à relire | យល់ព្រម និងបង់ប្រាក់ | Accept & Pay | sale |
| ⏳ à relire | ចំនួនបានបង់៖ | Amount paid: | sale |
| ⏳ à relire | កាលបរិច្ឆេទដឹកជញ្ជូន៖ | Delivery Date: | sale |
| ⏳ à relire | ឯកសារ | Documents | sale |
| ⏳ à relire | ប្រាក់កក់ | Down payment | sale |
| ⏳ à relire | ចំនួនពេញ | Full amount | sale |
| ⏳ à relire | រួមពន្ធ) | Incl. tax) | sale |
| ⏳ à relire | ការបញ្ជាទិញមិនត្រឹមត្រូវ។ | Invalid order. | sale |
| ⏳ à relire | ទិន្នន័យហត្ថលេខាមិនត្រឹមត្រូវ។ | Invalid signature data. | sale |
| ⏳ à relire | អាសយដ្ឋានចេញវិក្កយបត្រ | Invoicing Address | sale |
| ⏳ à relire | វិក្កយបត្រចុងក្រោយ | Last Invoices | sale |
| ⏳ à relire | កាលបរិច្ឆេទបញ្ជាទិញ | Order Date | sale |
| ⏳ à relire | កាលបរិច្ឆេទបញ្ជាទិញ៖ | Order Date: | sale |
| ⏳ à relire | ការបញ្ជាទិញចុះហត្ថលេខាដោយ %s | Order signed by %s | sale |
| ⏳ à relire | បង់ការបញ្ជាទិញ | Pay Order | sale |
| ⏳ à relire | លក្ខខណ្ឌទូទាត់ | Payment terms | sale |
| ⏳ à relire | សម្រង់តម្លៃលេខ | Quotation # | sale |
| ⏳ à relire | កាលបរិច្ឆេទសម្រង់តម្លៃ | Quotation Date | sale |
| ⏳ à relire | សម្រង់តម្លៃបានផ្ញើ | Quotation Sent | sale |
| ⏳ à relire | ការបញ្ជាទិញ | Sales Order | sale |
| ⏳ à relire | អាសយដ្ឋានដឹកជញ្ជូន | Shipping Address | sale |
| ⏳ à relire | ចុះហត្ថលេខា និងបង់ប្រាក់ | Sign & Pay | sale |
| ⏳ à relire | ខ្វះហត្ថលេខា។ | Signature is missing. | sale |
| ⏳ à relire | ចាប់ផ្តើមប្រើ Odoo | Start on Odoo | sale |
| ⏳ à relire | សូមប្រាប់យើងពីមូលហេតុដែលលោកអ្នកបដិសេធសម្រង់តម្លៃនេះ ដើម្បីជួយយើងកែលម្អសេវាកម្ម។ | Tell us why you are refusing this quotation, this will help us improve our services. | sale |
| ⏳ à relire | លក្ខខណ្ឌទូទៅ | Terms & Conditions | sale |
| ⏳ à relire | ការបញ្ជាទិញនេះមិនស្ថិតក្នុងស្ថានភាពដែលត្រូវការការទូទាត់ពីអតិថិជនទេ។ | The order is not in a state requiring customer payment. | sale |
| ⏳ à relire | ការបញ្ជាទិញនេះមិនស្ថិតក្នុងស្ថានភាពដែលត្រូវការហត្ថលេខាអតិថិជនទេ។ | The order is not in a state requiring customer signature. | sale |
| ⏳ à relire | បច្ចុប្បន្នមិនមានការបញ្ជាទិញសម្រាប់គណនីរបស់លោកអ្នកទេ។ | There are currently no sales orders for your account. | sale |
| ⏳ à relire | មានសុពលភាពដល់ | Valid Until | sale |
| ⏳ à relire | ការបញ្ជាទិញរបស់លោកអ្នកត្រូវបានបញ្ជាក់ហើយ។ | Your order has been confirmed. | sale |
| ⏳ à relire | ការបញ្ជាទិញរបស់លោកអ្នកបានចុះហត្ថលេខាហើយ ប៉ុន្តែត្រូវបង់ប្រាក់សិន ទើបត្រូវបានបញ្ជាក់។ | Your order has been signed but still needs to be paid to be confirmed. | sale |
| ⏳ à relire | ការបញ្ជាទិញរបស់លោកអ្នកបានចុះហត្ថលេខាហើយ។ | Your order has been signed. | sale |
| ⏳ à relire | ការបញ្ជាទិញរបស់លោកអ្នកមិនស្ថិតក្នុងស្ថានភាពដែលអាចបដិសេធបានទេ។ | Your order is not in a state to be rejected. | sale |
| ⏳ à relire | លោកអ្នកបញ្ជាក់ការយល់ព្រមក្នុងនាម | you confirm acceptance on behalf of | sale |
| ⏳ à relire | បន្ថែមមួយ | Add one | sale_management |
| ⏳ à relire | ដកមួយ | Remove one | sale_management |
| ⏳ à relire | កំពុងរង់ចាំមកដល់ | Awaiting arrival | sale_stock |
| ⏳ à relire | កំពុងរៀបចំ | Preparation | sale_stock |
| ⏳ à relire | បានទទួល | Received | sale_stock |
| ⏳ à relire | បានដឹកចេញ | Shipped | sale_stock |
| ⏳ à relire | បានដឹកជញ្ជូន | Delivered | sale_stock |
| ⏳ à relire | ការដឹកជញ្ជូនចុងក្រោយ | Last Delivery Orders | sale_stock |
| ⏳ à relire | មិនទាន់ដឹកជញ្ជូន | Not Delivered | sale_stock |
| ⏳ à relire | បានដឹកជញ្ជូនមួយផ្នែក | Partially Delivered | sale_stock |
| ⏳ à relire | ការបង្វិលត្រឡប់ | RETURN | sale_stock |
| ⏳ à relire | ការបង្វិលត្រឡប់ | Returns | sale_stock |
| ⏳ à relire | ស្ថានភាពដឹកជញ្ជូន | Shipping Status | sale_stock |
| ⏳ à relire | បានចាប់ផ្តើម | Started | sale_stock |
| ⏳ à relire | ថ្ងៃ | Days | uom |
| ⏳ à relire | ឡូ | Dozens | uom |
| ⏳ à relire | %s ឯកសារ | %s Files | web |
| ⏳ à relire | ទទួលយក និងចុះហត្ថលេខា | Adopt & Sign | web |
| ⏳ à relire | កំណត់ហត្ថលេខារបស់លោកអ្នក | Adopt Your Signature | web |
| ⏳ à relire | ការជូនដំណឹង | Alert | web |
| ⏳ à relire | មានកំហុសកើតឡើងពេលផ្ទុកឡើង។ | An error occured while uploading. | web |
| ⏳ à relire | ស្វ័យប្រវត្តិ | Auto | web |
| ⏳ à relire | ដោយចុច «ទទួលយក និងចុះហត្ថលេខា» ខ្ញុំយល់ព្រមថា ហត្ថលេខា ឬអក្សរកាត់ដែលបានជ្រើសរើស គឺជាតំណាងអេឡិចត្រូនិកដែលមានសុពលភាព នៃហត្ថលេខា ឬអក្សរកាត់សរសេរដោយដៃរបស់ខ្ញុំ សម្រាប់គ្រប់គោលបំណង នៅពេលប្រើលើឯកសារ រួមទាំងកិច្ចសន្យាដែលមានកាតព្វកិច្ចផ្លូវច្បាប់។ | By clicking Adopt & Sign, I agree that the chosen signature/initials will be a valid electronic representation of my hand-written signature/initials for all purposes when it is used on documents, including legally binding contracts. | web |
| ⏳ à relire | បោះបង់ការផ្ទុកឡើង | Cancel Upload | web |
| ⏳ à relire | Caps Lock កំពុងបើក! | Caps Lock is on! | web |
| ⏳ à relire | ឈ្មោះក្រុមហ៊ុន | Company name | web |
| ⏳ à relire | រក្សាសិទ្ធិ &copy; | Copyright &copy; | web |
| ⏳ à relire | តើលោកអ្នកពិតជាចង់បោះបង់ការផ្ទុកឡើង %s មែនទេ? | Do you really want to cancel the upload of %s? | web |
| ⏳ à relire | គូរ | Draw | web |
| ⏳ à relire | ឈ្មោះពេញ | Full Name | web |
| ⏳ à relire | ផ្ទុករូបភាព | Load | web |
| ⏳ à relire | ចាកចេញ | Log out | web |
| ⏳ à relire | ចូលគណនី | Login | web |
| ⏳ à relire | វគ្គប្រើប្រាស់ផុតកំណត់ | Odoo Session Expired | web |
| ⏳ à relire | យល់ព្រម | Ok | web |
| ⏳ à relire | ដំណើរការដោយ %s%s | Powered by %s%s | web |
| ⏳ à relire | ដំណើរការដោយ Odoo | Powered by Odoo | web |
| ⏳ à relire | កំពុងដំណើរការ... | Processing... | web |
| ⏳ à relire | សំណើអស់ពេល | Request timeout | web |
| ⏳ à relire | ប្រតិបត្តិការត្រូវបានរំខាន។ ជាធម្មតា នេះមានន័យថាប្រតិបត្តិការបច្ចុប្បន្នចំណាយពេលយូរពេក។ | The operation was interrupted. This usually means that the current operation is taking too much time. | web |
| ⏳ à relire | ឯកសារនេះមិនត្រឹមត្រូវ។ សូមជ្រើសរើសរូបភាព។ | This file is invalid. Please select an image. | web |
| ⏳ à relire | វាយឈ្មោះរបស់លោកអ្នកដើម្បីចុះហត្ថលេខា | Type your name to sign | web |
| ⏳ à relire | កំពុងផ្ទុកឡើង... (%s%) | Uploading... (%s%) | web |
| ⏳ à relire | ឈ្មោះចូល ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវ | Wrong login/password | web |
| ⏳ à relire | លោកអ្នកបានចូលគណនីហើយ។ | You are logged in. | web |
| ⏳ à relire | វគ្គប្រើប្រាស់របស់លោកអ្នកផុតកំណត់ហើយ។ ទំព័រនេះនឹងត្រូវផ្ទុកឡើងវិញ។ | Your Odoo session expired. The current page is about to be refreshed. | web |
| ⏳ à relire | កំពុងទាញយក... | downloading... | web |
| ⏳ à relire | លិខិតឥណទាន | Credit Note | account |
| ⏳ à relire | លិខិតឥណទានព្រាង | Draft Credit Note | account |
| ⏳ à relire | វិក្កយបត្រ | Invoice | account |
| ⏳ à relire |  |  | auth_totp_portal, payment, portal |
| ⏳ à relire | ប្រសិនបើលោកអ្នកគិតថានេះជាកំហុស សូមទាក់ទងអ្នកគ្រប់គ្រងគេហទំព័រ។ | If you believe that it is an error, please contact the website administrator. | payment |
