#!/usr/bin/python
#
#
#  Strip images from flickr because those wingo dingos dont like to share
#
#
from BeautifulSoup  import BeautifulSoup as Soup
from argparse       import ArgumentParser 
from PyQt4.QtGui    import *
from PyQt4.QtCore   import *
from PyQt4.QtWebKit import *
import sys, re, urllib2


class Unflickr( object ):

    class RenderPage( QWebPage ):
        """
            Render page via Qt 
        """

        def __init__( self, url ):
            self.app = QApplication( sys.argv )
            QWebPage.__init__( self )

            self.loadFinished.connect( self._callback )
            self.mainFrame().load( QUrl( url ) )
            self.app.exec_()

        def _callback( self, result ):
            self.frame = self.mainFrame()
            self.app.quit()


    def stripId( self, url = None ):
        """
            Strip id from url
        """

        return re.findall( "photos\/(.*)\/([0-9]{10,11})\/", url )[0]


    def stripImg( self, html = None ):
        """
            Strip Image Link From Html Block
        """

        return re.findall( "img\](.*)\[\/img", str( html ) )[0]

    def imageFromUrl( self, url = None ):
        """
            Given a url strip the image id and location 
        """

        if url is None: 
            return "A Url is required to use this call"
        
        rendered = self.RenderPage( url )
        html     = rendered.frame.toHtml().toUtf8()
        soup     = Soup( ''.join( html ) )
        imgBlock = soup.findAll( 'textarea', { 'name' : 'SharingEmbedMarkupLBBCode' } )[0] 
        Id       = self.stripId(  url )
        
        imgUrl   = self.stripImg( imgBlock )

        return ( "-".join( Id ), imgUrl )


if __name__ == "__main__":

    unflickr = Unflickr()

    parser = ArgumentParser( description="Steal Protected Flickr Images" )

    parser.add_argument( '-u', '--url',    dest="url",      default=None, help="URL to strip image from" )
    parser.add_argument( '-o', '--output', dest="filename", default=None, help="Path to store Image"     )

    args = parser.parse_args()

    if args.url is not None:
        imgMeta = unflickr.imageFromUrl( args.url ) 

        with open( imgMeta[ 0 ] if args.filename is None else args.filename, "wb" ) as fd:
            fd.write( urllib2.urlopen( imgMeta[ 1 ] ).read() )
