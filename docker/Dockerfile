# Image Odoo 19.0 Community officielle, épinglée par empreinte.
# Pour mettre à jour : docker pull odoo:19.0, relever la nouvelle empreinte
# (docker image inspect odoo:19.0 --format '{{index .RepoDigests 0}}'),
# la reporter ici et dans docs/MODULES.md.
FROM odoo:19.0@sha256:03a47921f9eef2c225ded1167fe7828465d2b3177883f30d173bb1c3c792949b

USER root

# Polices khmères pour les PDF (Noto Sans Khmer / Noto Serif Khmer).
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-noto-core \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f

# Code : modules OCA (sous-modules git) et modules maison.
# En local, docker-compose.local.yml remplace ces copies par des montages.
COPY oca /opt/chantrea/oca
COPY addons /opt/chantrea/addons
COPY docker/entrypoint-chantrea.sh /usr/local/bin/entrypoint-chantrea.sh
RUN chmod 755 /usr/local/bin/entrypoint-chantrea.sh

USER odoo

ENTRYPOINT ["/usr/local/bin/entrypoint-chantrea.sh"]
CMD ["odoo"]
