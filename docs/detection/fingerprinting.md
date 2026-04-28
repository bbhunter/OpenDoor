# 🧬 Fingerprinting

Fingerprinting attempts to identify probable technologies before or during a scan.

Enable it with:

```shell
opendoor --host https://example.com --fingerprint
```

---

## What fingerprinting helps with

Fingerprinting can help identify probable:

- CMS platforms;
- e-commerce platforms;
- frameworks and application platforms;
- site builders;
- static-site and documentation generators;
- hosting platforms;
- infrastructure providers;
- CDN or edge infrastructure signals.

This helps you choose better wordlists, filters, and scan strategy.

---

## Basic example

```shell
opendoor --host https://example.com --fingerprint
```

Combine with directory discovery:

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --scan directories
```

---

## Fingerprinting with reports

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --reports json,html
```

Use machine-readable reports when you want to process detected technologies later.

---

## Fingerprinting and scan strategy

A detected technology can influence:

| Signal | Possible scan adjustment |
|---|---|
| CMS | Use CMS-specific wordlists |
| Static hosting | Focus on exposed files and deployment artifacts |
| CDN or edge provider | Enable WAF detection and safer request settings |
| Framework | Scan common framework routes and asset paths |
| Admin panel signal | Focus on auth and restricted resources |

---

## Recognized systems

The heuristic fingerprint engine currently recognizes the following platform families.

### CMS

- Bitrix
- Bludit
- Bolt CMS
- Concrete CMS
- Contao
- Craft CMS
- Directus
- Discourse
- Drupal
- Ghost
- GravCMS
- Joomla
- Matomo
- MediaWiki
- Open Journal Systems
- MODX
- Moodle
- Neos
- Nextcloud
- OctoberCMS
- ownCloud
- phpBB
- phpMyAdmin
- Pimcore
- TYPO3
- Umbraco
- WordPress

### E-commerce

- Magento
- nopCommerce
- OpenCart
- PrestaShop
- Shopify
- Shopware
- WooCommerce

### Frameworks and app platforms

- Angular
- ASP.NET
- Astro
- Django
- Express
- FastAPI
- Fastify
- Flask
- Gatsby
- Hapi
- Koa
- Laravel
- NestJS
- Next.js
- Nuxt
- Phoenix
- React
- Remix
- Ruby on Rails
- Spring
- Strapi
- SvelteKit
- Symfony
- Vue

### Site builders

- Squarespace
- Tilda
- Webflow
- Wix

### Static and docs generators

- Docusaurus
- Hugo
- Jekyll
- MkDocs
- VitePress

### Infrastructure providers and hosting edge signals

- AWS
- AWS API Gateway
- AWS Amplify
- AWS CloudFront
- AWS ELB / ALB
- AWS S3
- Akamai
- Cloudflare
- Fastly
- GitHub Pages
- GitLab Pages
- Google App Engine
- Google Cloud
- Google Cloud / Google Frontend
- Google Cloud Run
- Heroku
- Microsoft Azure
- Microsoft Azure App Service
- Netlify
- OpenResty
- Vercel

---

## Recommended workflow

```shell
opendoor \
  --host https://example.com \
  --fingerprint \
  --auto-calibrate \
  --reports std,json,csv
```

This gives a better initial view of the target before deeper scans.

---

## Notes

Fingerprinting is heuristic. Treat results as probable signals, not as guaranteed facts.

Always verify important findings manually.

For WAF and anti-bot detection, see [WAF detection and safe mode](waf-detection.md).
