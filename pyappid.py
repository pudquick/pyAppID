#!/usr/bin/env python
"""Usage: pyappid [OPTION]... PATH

List information about the iTunes iOS App Store .ipa files located in PATH.
Output is a tab separated column format, with default outputs:
 * iTunes & App Store Display Name (a)
 * iOS Screen Display Name (s)
 * iTunes App Store ID (i)

Options:
  -h, --help                 Display this message
  -c, --columns COLUMNS      Comma separated list of attributes to display
  -s, --sort ATTRIBUTE       Sort by specified attribute
  -o, --output FILE          Save output to specified file instead of stdout
  -i, --ignore               Ignore problematic .ipa files instead of stopping
  -v, --verbose              Enable verbose debug logging

App Store attributes available:
   a - iTunes & App Store Display Name
   s - iOS Screen Display Name (when installed on device)
   i - iTunes App Store ID
   p - path to the .ipa file being parsed
   b - name of the .app bundle in the .ipa file

Example usage:
   Display current apps: pyappid "~/Music/iTunes/Mobile Applications"
   Display only iOS name and ID, sorted by ID: pyappid -c s,i -s i PATH"""

from __future__ import with_statement

import sys, getopt, glob, os.path, zipfile, re, warnings, csv, types, tempfile, codecs, cStringIO

try:
    # On a Mac? Use native Foundation library wrappers
    from FoundationPlist import readPlistFromString
except:
    # Whoops, guess that didn't work. Fall back to pblistlib
    from bplistlib import readPlistFromString

def usage():
    print __doc__
    sys.exit()

def main():
    available_columns = ['a', 's', 'i', 'p', 'b', 'v']
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:s:o:i", ["help", "verbose", "columns=","sort=","output=","ignore"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
    columns,sort,output = None,None,None
    ignore,verbose = False, False
    path = ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-c", "--columns"):
            columns = []
            for x in a.split(','):
                # Only print at most one of a particular attribute column
                if x and (not (x in columns)):
                    columns.append(x)
            for x in columns:
                if (x not in available_columns):
                    print "'%s' is not an available attribute" % x
                    usage()
            if (not columns):
                print "at least one attribute must be specified"
                usage()
        elif o in ("-s", "--sort"):
            if (not (a in available_columns)):
                print "'%s' is not an available attribute" % a
                usage()
            sort = a
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-i", "--ignore"):
            ignore = True
        elif o in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "Unhandled option. Contact the developer."
    if (not len(args)):
        print "Error: PATH is required"
        usage()
    path = args[0]
    return process_ipas(path,columns,sort,output,ignore,verbose)

def get_app_info(app):
    try:
        if (not zipfile.is_zipfile(app)):
            return False
    except:
        return False
    zapp = zipfile.ZipFile(app, 'r')
    # Extract the iTunesMetadata.plist
    try:
        # Try to find it safely
        itmd_name = "iTunesMetadata.plist"
        files = zapp.namelist()
        for f in files:
            if (f.lower() in ["itunesmetadata.plist", "./itunesmetadata.plist"]):
                itmd_name = f
        itmd = zapp.read(itmd_name)
    except:
        print "Error: iTunesMetadata.plist not found"
        return False
    # print itmd
    # Now for the hard one - finding the Info.plist
    possible_infos = []
    bundle_name = ''
    try:
        # Filter it down to info.plist files first
        valid_bundle = re.compile(r"((./)?payload/[^/]+.app)", re.I)
        for f in files:
            lf = f.lower()
            if (valid_bundle.search(f)):
                bundle_name = valid_bundle.search(f).group(0)
            if (lf.endswith(".app/info.plist") and (lf.startswith("payload/") or lf.startswith("./payload/"))):
                if (not (f in possible_infos)):
                    possible_infos.append(f)
        valid_info = re.compile(r"(./)?payload/[^/]+.app/info.plist", re.I)
        real_infos = []
        for f in possible_infos:
            if (valid_info.match(f)):
                real_infos.append(f)
        if (len(real_infos) != 1):
            print "Error: More than one Payload/*.app/Info.plist found"
            return False
        infop = zapp.read(real_infos[0])
    except:
        print "Error: Payload/*.app/Info.plist not found"
    # Find the .app bundle name, for apps that don't have a CFBundleDisplayName

    # print infop
    d_app = dict()
    d_app['p'] = os.path.basename(app)
    try:
        d_app['b'] = bundle_name.split("/")[-1].rsplit(".")[0]
    except:
        d_app['b'] = bundle_name
    try:
        with warnings.catch_warnings():
            # This is to wrap out an annoying warning in the pblistlib
            warnings.filterwarnings("ignore",category=DeprecationWarning)
            info_d = readPlistFromString(infop)
            itmd_d = readPlistFromString(itmd)
    except:
        print "Error: One or more malformed .plist files in .ipa"
        return False
    info_columns = {'s': 'CFBundleDisplayName', 'v': 'UIBackgroundModes'}
    itmd_columns = {'a': 'itemName', 'i': 'itemId'}
    for i in info_columns.keys():
        if (i == 'v'):
            b_modes = list(info_d.get(info_columns[i], []))
            b_modes = [x.lower() for x in b_modes]
            if ('voip' in b_modes):
                d_app[i] = "VOIP-YES"
            else:
                d_app[i] = "VOIP-NO"
        else:
            d_app[i] = info_d.get(info_columns[i], None)
        # Fix for lack of CFBundleDisplayName
        if ((i == 's') and (d_app[i] == None)):
            d_app[i] = d_app['b']
    for i in itmd_columns.keys():
        d_app[i] = itmd_d.get(itmd_columns[i], None)
        if (i == 'i'):
            d_app[i] = int(d_app[i])
    return tuple(sorted(d_app.items(), key=lambda x: x[0]))

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        temp = []
        for s in row:
            if (type(s) == types.IntType):
                temp.append(str(s))
            else:
                temp.append(s)
        self.writer.writerow([s.encode("utf-8") for s in temp])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def process_ipas(path,columns,sort,output,ignore,verbose):
    if (not (os.path.isdir(path))):
        print "'%s' does not appear to be a valid path" % path
        sys.exit()
    apps = glob.glob(os.path.join(path, '*.ipa'))
    if (not apps):
        print "'%s' does not appear to contain any .ipa files" % path
        sys.exit()
    app_infos = set()
    for app in apps:
        if verbose:
            print "DEBUG: Processing:", app
        info = get_app_info(app)
        if (info):
            app_infos.add(info)
        else:
            if (not ignore):
                print "'%s' does not appear to be a valid .ipa file" % app
                sys.exit()
    if (not app_infos):
        print "no iTunes App Store apps found"
        sys.exit()
    # Convert our unique set of apps back into a list of dicts, default sort on lower app name
    apps = sorted([dict(app) for app in list(app_infos)], key=lambda x: x['a'].lower())
    # Re-sort if a sorting key was specified
    if (sort):
        # Check for string or int key value
        if (type(apps[0][sort]) == types.IntType):
            apps = sorted(apps, key=lambda x: x[sort])
        else:
            apps = sorted(apps, key=lambda x: x[sort].lower())
    if (output):
        outfile = open(output, 'wb')
    else:
        outfile = tempfile.TemporaryFile()
    csv.register_dialect('exceltab', delimiter='\t')
    # Fix for Unicode characters
    # writer = csv.writer(outfile, dialect='exceltab')
    writer = UnicodeWriter(outfile, dialect='exceltab')
    order = ['a','s','i']
    if (columns):
        order = columns
    for app in apps:
        if verbose:
            print "DEBUG: Raw data:", app
        data = [app.get(key,'') for key in order]
        if verbose:
            print "DEBUG: Sorted data:", data
        writer.writerow(data)
    if (not output):
        outfile.seek(0)
        print outfile.read(),
    outfile.close()

if __name__ == "__main__":
    main()

# http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=#####&mt=8
