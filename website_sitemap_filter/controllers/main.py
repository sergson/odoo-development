import datetime
from itertools import islice
import logging

import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp.addons.website.controllers.main import SITEMAP_CACHE_TIME, LOC_PER_SITEMAP

_logger = logging.getLogger(__name__)


class Website(openerp.addons.web.controllers.main.Home):

    @http.route('/sitemap.xml', type='http', auth="public", website=True)
    def sitemap_xml_index(self):
        current_website = request.website
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        ira = request.registry['ir.attachment']
        iuv = request.registry['ir.ui.view']
        mimetype ='application/xml;charset=utf-8'
        content = None

        def create_sitemap(url, content):
            return ira.create(cr, uid, dict(
                datas=content.encode('base64'),
                mimetype=mimetype,
                type='binary',
                name=url,
                url=url,
            ), context=context)
        dom = [('url', '=' , '/sitemap-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = ira.search_read(cr, uid, dom, ('datas', 'create_date'), context=context)
        if sitemap:
            # Check if stored version is still valid
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            create_date = datetime.datetime.strptime(sitemap[0]['create_date'], server_format)
            delta = datetime.datetime.now() - create_date
            if delta < SITEMAP_CACHE_TIME:
                content = sitemap[0]['datas'].decode('base64')

        if not content:
            # Remove all sitemaps in ir.attachments as we're going to regenerated them
            dom = [('type', '=', 'binary'), '|', ('url', '=like' , '/sitemap-%d-%%.xml' % current_website.id),
                   ('url', '=' , '/sitemap-%d.xml' % current_website.id)]
            sitemap_ids = ira.search(cr, uid, dom, context=context)
            if sitemap_ids:
                ira.unlink(cr, uid, sitemap_ids, context=context)

            pages = 0
            locs = request.website.sudo(user=request.website.user_id.id).enumerate_pages()

            # if handled in model, it won't show urls when searched for linking.
            if request.website.exclude_from_sitemap:
                exclude_from_sitemap = request.website.exclude_from_sitemap.splitlines()

                raw_locs = locs;
                locs = []

                for loc in raw_locs:
                    lloc = loc.values()

                    if lloc[0] in exclude_from_sitemap:
                        _logger.info("Excluding: %s" % lloc[0])
                    else:
                        locs.append(loc)

            while True:
                start = pages * LOC_PER_SITEMAP
                values = {
                    'locs': islice(locs, start, start + LOC_PER_SITEMAP),
                    'url_root': request.httprequest.url_root[:-1],
                }
                urls = iuv.render(cr, uid, 'website.sitemap_locs', values, context=context)
                if urls.strip():
                    content = iuv.render(cr, uid, 'website.sitemap_xml', dict(content=urls), context=context)
                    pages += 1
                    last = create_sitemap('/sitemap-%d-%d.xml' % (current_website.id, pages), content)
                else:
                    break
            if not pages:
                return request.not_found()
            elif pages == 1:
                # rename the -id-page.xml => -id.xml
                ira.write(cr, uid, last, dict(url="/sitemap-%d.xml" % current_website.id, name="/sitemap-%d.xml" % current_website.id), context=context)
            else:
                # TODO: in master/saas-15, move current_website_id in template directly
                pages_with_website = map(lambda p: "%d-%d" % (current_website.id, p), range(1, pages + 1))

                # Sitemaps must be split in several smaller files with a sitemap index
                content = iuv.render(cr, uid, 'website.sitemap_index_xml', dict(
                    pages=pages_with_website,
                    url_root=request.httprequest.url_root,
                ), context=context)
                create_sitemap('/sitemap-%d.xml' % current_website.id, content)

        return request.make_response(content, [('Content-Type', mimetype)])
