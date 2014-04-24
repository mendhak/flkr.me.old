import httplib
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from flickrtools import flickrapi
import datetime
import re


#https://docs.djangoproject.com/en/dev/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-don-t-use-the-standard-names
#This 'view' corresponds to the MVC 'controller'.



apiKey = "a39dfdf51784c76fa3234f88bec38b0e"

def image(request, nsid, num=1, size='', popular=''):
    if not num or not num.isdigit() or int(num) <= 0:
        num = 1
    if not size:
        size = 's'
    if not popular:
        popular = ''

    cacheKey = "image"+nsid+num+size+popular
    resp = HttpResponse(status=302)
    cachedResponse = cache.get(cacheKey)

    if cachedResponse:
        resp = cachedResponse
    else:
        nsid = getUserNSID(request, resp, apiKey, nsid)
        photo = flickrapi.getPhoto(apiKey, nsid, num, popular)
        destinationUrl = flickrapi.getImageUrl(photo, size)
        resp['Title'] = photo.title.encode("utf-8")
        resp['Location'] = destinationUrl
        cache.add(cacheKey, resp, 60*15)
    return resp


def searchImage(request, tags='', num=1, size='', nsid=''):
    if not num or not num.isdigit() or int(num) <= 0:
        num = 1
    if not size:
        size = 's'

    resp = HttpResponse(status=302)
    nsid = getUserNSID(request, resp, apiKey, nsid)
    photo = flickrapi.getPhotoBySearch(apiKey, nsid, tags, num)
    destinationUrl = flickrapi.getImageUrl(photo, size)
    resp['Title'] = photo.title.encode("utf-8")
    resp['Location'] = destinationUrl
    return resp


def searchRedirect(request, tags='', num=1, nsid=''):
    if not num or not num.isdigit() or int(num) <= 0:
        num = 1
    resp = HttpResponse(status=302)
    nsid = getUserNSID(request, resp, apiKey, nsid)
    photo = flickrapi.getPhotoBySearch(apiKey, nsid, tags, num)
    destinationUrl = flickrapi.getPhotoPageUrl(photo, nsid)
    resp['Title'] = photo.title.encode("utf-8")
    resp['Location'] = destinationUrl
    return resp

def redirect(request, nsid, num, popular):
    if not num or not num.isdigit() or int(num) <= 0:
        num = 1
    if not popular:
        popular = ''

    cacheKey = "redirect"+nsid+num+popular
    resp = HttpResponse(status=302)
    cachedResponse = cache.get(cacheKey)

    if cachedResponse:
        resp = cachedResponse
    else:
        resp = HttpResponse(status=302)
        nsid = getUserNSID(request, resp, apiKey, nsid)
        photo = flickrapi.getPhoto(apiKey, nsid, num, popular)
        destinationUrl = flickrapi.getPhotoPageUrl(photo, nsid)
        resp['Title'] = photo.title.encode("utf-8")
        resp['Location'] = destinationUrl
        cache.add(cacheKey, resp, 60*15)
    return resp

@cache_page(60 * 15)
def nsid(request, username):
    resp = HttpResponse()
    nsid = getUserNSID(request, resp, apiKey, username)
    resp.write(nsid)
    return resp


def readTitleFromHeader(url):
    #Manually parse URL, Apache may remove double slashes
    lastSlash = url.rfind('/', 0, 8)
    pathPos = url.find('/', lastSlash + 1)

    if pathPos > -1:
        conn = httplib.HTTPConnection(str(url[lastSlash + 1:pathPos]))
        conn.request("HEAD", str(url[pathPos:]))
        res = conn.getresponse()
        title = res.getheader('Title')

    if title is None:
        title = ""

    return title

@cache_page(60 * 15)
def getTitleFromUrl(request, url):
    resp = HttpResponse()
    title = readTitleFromHeader(url)
    resp.write(title)
    return resp


def getUserNSID(request, response, apiKey, username):
    if username is None:
        return ''

    if 'http://' in username or 'www.' in username:
        userRegex = re.compile(r'photos/(?P<username>[^/]+)')
        m = userRegex.search(username)
        username = m.group('username')

    cookies = request.COOKIES
    cookieKey = str('nsid_' + username)
    nsidRegex = re.compile("([0-9]+@N[0-9]+)")

    if cookies.has_key(cookieKey):
        nsid = cookies[cookieKey]
    elif not nsidRegex.match(username) and not cookieKey in cookies:
        nsid = flickrapi.getNSID(apiKey, username)
        setCookie(response, cookieKey, nsid)
    else:
        nsid = username

    return nsid


def showcolor(request, color, photoid):

    flickrPhotoId = getPhotoId(photoid, request)

    if not flickrPhotoId:
        raise Http404

    photoUrl = flickrapi.getLargestSizeUrl("b4fe2a004c947c42b2be8f2796796105", flickrPhotoId)

    if not photoUrl:
        raise Http404

    returnUrl = "http://www.flickr.com/photo.gne?id=" + flickrPhotoId

    fullWidth = False

    if color.lower() == "full":
        fullWidth = True

    return render_to_response('display.html', {'hexColor': '#000000', 'photoUrl': photoUrl, 'returnUrl': returnUrl,
                                               'fullWidth': fullWidth}, context_instance=RequestContext(request))


def getPhotoId(photoId, request):
    if photoId:
        return photoId

    if request:
        referrer = getReferrerFromRequest(request)
        photoId = flickrapi.getPhotoIdFromUrl(referrer)
        return photoId


def getReferrerFromRequest(req):
    if "HTTP_REFERER" in req.META:
        return req.META["HTTP_REFERER"]

    return None


def fullscreen(request):
    resp = HttpResponse()
    return render_to_response('bg.html', {'domain': request.get_host()}, context_instance=RequestContext(request))


def main(request):
    return render_to_response('sig.html', {'domain': request.get_host()}, context_instance=RequestContext(request))


def setCookie(response, cookieKey, nsid, expire=None):
    if expire is None:
        max_age = 365 * 24 * 60 * 60
    else:
        max_age = expire
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key=str(cookieKey), value=nsid, max_age=max_age, expires=expires, domain=None, secure=False)

