"""
Python script for retrieving data for the NewsML-G2 specifications (as AsciiDoctor file)
  from a specific Google sheet document.
The retrieved data are transformed to AsciiDoctor format

For IPTC-internal use
Creator: Michael Steidl

History:
    2017-08-30 MS: adapted from PMD XMP Schema transformation
"""

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def writeSpecDoc(service, spreadsheetId, rangeName, fromRow, toRow, columncount, outputFN):

    # retrieve the values from the spreadsheet
    result1 = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result1.get('values', [])


    # open the Asciidoc document
    outputFP = ".//_includes//tables//" + outputFN
    with open(outputFP, "w", encoding='utf-8') as outf:
        # iterate over the rows
        createTableHeading = True
        for rowcounter in range(fromRow, toRow):
            if (createTableHeading):
                # Table heading is created from the first line of the table
                outf.write("[%autowidth,options=\"header\"]\n")
                outf.write("|===\n")
                rowline = ""
                for columncounter in range(0, columncount):
                    try:
                        valstr = values[rowcounter][columncounter]
                    except:
                        valstr = ' '
                    rowline += "|" + valstr

                outf.write(rowline + "\n")
                outf.write("\n")
                createTableHeading = False
            else:
                # the table rows are created
                for columncounter in range(0, columncount):
                    try:
                        valstr = values[rowcounter][columncounter]
                    except:
                        valstr = ' '
                    cellvalue = valstr.strip('\r')
                    cellvalue = cellvalue.replace("\n", " ")
                    cellvalue = cellvalue.replace("\t", " ")
                    cellvalue = "|" + cellvalue + "\n"
                    outf.write(cellvalue)

                outf.write("\n")

        # end of the table
        outf.write("|===\n")
        outf.close()


def main():
    """
    Step 1:
    Creates a Sheets API service object
    https://docs.google.com/spreadsheets/d/1qpfrNEu5urB1KUu1AlwRbd9NyNIADxZAgr0QNJnFYQo/edit
    = IPTC NewsML-G2 Specification Tables
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1qpfrNEu5urB1KUu1AlwRbd9NyNIADxZAgr0QNJnFYQo'

    # execute a writeSpecDoc function for each table:
    # function writeSpecDoc(service, spreadsheetId, rangeName, fromRow, toRow, columncount, outputFN)
    # use these parameters
    # service = service (stable, does not change for the different calls)
    # spreadsheetId = spreadsheetId (stable, does not change for the different calls)
    # rangeName = name of sheet tab + "!" + name of first column (e.g. A) + ":" + name of last column (e.g. M)
    # fromRow = Google sheet row number of the first row minus 1 (e.g. 0 for the first row = 1)
    # toRow = Google sheet row number
    # columncount = count of columns defined in the rangeName
    # outputFN = name of the output file. It REQUIRES as subfolder name "output" !!
    # see example(s) below

    # create file for the IIM-to-G2 tab
    writeSpecDoc(service, spreadsheetId, "Version-History!A:D", 0, 15, 4, "version-history.adoc")
    writeSpecDoc(service, spreadsheetId, "Item-Management!A:C", 0, 24, 3, "item-management.adoc")
    writeSpecDoc(service, spreadsheetId, "Embargo-Usable!A:C", 0, 7, 3, "embargo-usable.adoc")
    writeSpecDoc(service, spreadsheetId, "Administrative-Metadata!A:C", 0, 11, 3, "administrative-metadata.adoc")
    writeSpecDoc(service, spreadsheetId, "Descriptive-Metadata!A:C", 0, 11, 3, "descriptive-metadata.adoc")
    writeSpecDoc(service, spreadsheetId, "TimeUnit-Processing!A:C", 0, 5, 3, "timeunit-processing.adoc")
    writeSpecDoc(service, spreadsheetId, "iCalendar!A:B", 0, 27, 2, "icalendar.adoc")
    writeSpecDoc(service, spreadsheetId, "Relationship-Attributes!A:E", 0, 9, 5, "relationship-attributes.adoc")
    writeSpecDoc(service, spreadsheetId, "Descriptive-Meta-Core!A:C", 0, 7, 3, "descriptive-meta-core.adoc")
    writeSpecDoc(service, spreadsheetId, "Catalog-contentMeta!A:C", 0, 6, 3, "catalog-contentmeta.adoc")
    writeSpecDoc(service, spreadsheetId, "Namespaces!A:C", 0, 2, 3, "namespaces.adoc")
    writeSpecDoc(service, spreadsheetId, "Mime-Types!A:B", 0, 8, 2, "mime-types.adoc")
    writeSpecDoc(service, spreadsheetId, "Orientation-Values!A:C", 0, 9, 3, "orientation-values.adoc")
    writeSpecDoc(service, spreadsheetId, "Glossary!A:B", 0, 50, 2, "glossary.adoc")
    writeSpecDoc(service, spreadsheetId, "IPTC-Spec-Docs!A:B", 0, 5, 2, "iptc-spec-docs.adoc")
    writeSpecDoc(service, spreadsheetId, "Other-Refs!A:B", 0, 7, 2, "other-refs.adoc")
    writeSpecDoc(service, spreadsheetId, "Dimension-Unit-Defaults!A:C", 0, 5, 3, "dimension-unit-defaults.adoc")






if __name__ == '__main__':
    main()
