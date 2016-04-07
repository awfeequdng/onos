#!/usr/bin/env python
#FIXME Add license

##### Templates for features.xml
FEATURES_HEADER = '''\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<features xmlns="http://karaf.apache.org/xmlns/features/v1.2.0"
          name="%(feature_repo_name)s">
'''
FEATURE_HEADER= '''\
    <feature name="%(feature_name)s" version="%(version)s"
             description="%(title)s">
'''
EXISTING_FEATURE = '        <feature>%s</feature>\n'
BUNDLE = '        <bundle>%s</bundle>\n'
FEATURE_FOOTER = '    </feature>\n'
FEATURES_FOOTER = '</features>'

##### Templates for app.xml
APP_HEADER = '''\
<?xml version="1.0" encoding="UTF-8"?>
<app name="%(app_name)s" origin="%(origin)s" version="%(version)s"
        title="%(title)s" category="%(category)s" url="%(url)s"
        featuresRepo="%(feature_repo_name)s"
        features="%(feature_name)s" apps="%(apps)s">
    <description>%(description)s</description>
'''
ARTIFACT = '    <artifact>%s</artifact>\n'
APP_FOOTER = '</app>'


def mvnUrl(bundle):
    return 'mvn:' + bundle.replace(':', '/')

def generateFeatureFile(feature_name,
                        version,
                        title,
                        feature_repo_name,
                        features = [],
                        bundles = [],
                        **kwargs):
    values = {
        'feature_name' : feature_name,
        'version' : version,
        'title' : title,
        'feature_repo_name' : '-'.join(feature_repo_name.split(':')[1:3]),
    }

    output = FEATURES_HEADER % values + FEATURE_HEADER % values

    for feature in features:
        output += EXISTING_FEATURE % feature

    for bundle in bundles:
        output += BUNDLE % mvnUrl(bundle)

    output += FEATURE_FOOTER + FEATURES_FOOTER
    return output

def generateAppFile(app_name,
                    origin,
                    version,
                    title,
                    category,
                    url,
                    feature_repo_name,
                    feature_name,
                    description = None,
                    apps = [],
                    artifacts = [],
                    **kwargs):
    values = {
        'app_name' : app_name,
        'origin' : origin,
        'version' : version,
        'title' : title,
        'category' : category,
        'url' : url,
        'feature_repo_name' : mvnUrl(feature_repo_name) + '/xml/features',
        'feature_name' : feature_name,
    }

    values['description'] = description if description else title
    values['apps'] = ','.join(apps) if apps else ''

    output = APP_HEADER % values

    for artifact in artifacts:
        output += ARTIFACT % mvnUrl(artifact)

    output += APP_FOOTER
    return output


if __name__ == '__main__':
    import sys, optparse

    parser = optparse.OptionParser()
    parser.add_option("-n", "--name",     dest="feature_name", help="Feature Name")
    parser.add_option("-a", "--app",      dest="app_name",     help="App Name")
    parser.add_option("-o", "--origin",   dest="origin",       help="Origin")
    parser.add_option("-c", "--category", dest="category",     help="Category")
    parser.add_option("-u", "--url",      dest="url",          help="URL")
    parser.add_option("-v", "--version",  dest="version",      help="Version")
    parser.add_option("-t", "--title",    dest="title",        help="Title")
    parser.add_option("-r", "--repo",     dest="repo_name",    help="Repo Name")

    parser.add_option('-b', '--bundle',
                      action="append", dest='included_bundles',
                      metavar="BUNDLE", help='Included Bundle (multiple allowed)')
    parser.add_option('-e', '--excluded-bundle',
                      action="append", dest='excluded_bundles',
                      metavar="BUNDLE", help='Excluded Bundle (multiple allowed)')
    parser.add_option('-f', '--feature',
                      action="append", dest='features',
                      metavar="FEATURE", help='Existing Feature (multiple allowed)')
    parser.add_option('-d', '--apps',
                      action="append", dest='apps',
                      metavar="FEATURE", help='Required App (multiple allowed)')

    parser.add_option("-A", "--write-app", dest="write_app", action="store_true")
    parser.add_option("-F", "--write-features", dest="write_features", action="store_true")

    (options, args) = parser.parse_args()

    values = {}
    if options.feature_name and options.version and options.title:
        values['feature_name'] = options.feature_name.split(':')[1]
        values['version'] = options.version
        values['title'] = options.title
    else:
        sys.stderr.write('ERROR: Feature Name, Version, and Title are required\n')
        sys.stderr.flush()
        sys.exit(1)

    if options.app_name and options.origin and options.category and options.url:
        values['app_name'] = options.app_name
        values['origin'] = options.origin
        values['category'] = options.category
        values['url'] = options.url
    elif options.write_app:
        sys.stderr.write('ERROR: Feature Name, Version, and Title are required\n')
        sys.stderr.flush()
        sys.exit(1)

    values['feature_repo_name'] = options.repo_name if options.repo_name \
                                    else options.feature_name

    if options.write_features:
        bundles = []
        if options.included_bundles:
            bundles += options.included_bundles
        if options.excluded_bundles:
            bundles += options.excluded_bundles
        print generateFeatureFile(bundles=bundles,
                                  features=options.features,
                                  **values)
    if options.write_app:
        print generateAppFile(artifacts=options.included_bundles,
                              apps=options.apps,
                              **values)