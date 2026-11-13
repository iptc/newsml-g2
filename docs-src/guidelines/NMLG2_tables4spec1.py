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
    outputFP = ".//_includes//GuidelinesTables//" + outputFN
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
    https://docs.google.com/spreadsheets/d/1obfuedYo-dSbwZih432JskbbY3L5E6lspMgtdUlV5vM/edit
    = IPTC NewsML-G2 Guideline Tables
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1obfuedYo-dSbwZih432JskbbY3L5E6lspMgtdUlV5vM'

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
#    writeSpecDoc(service, spreadsheetId, "IIM-to-G2!A:D", 2, 25, 4, "IIM-to-G2.adoc")
#    writeSpecDoc(service, spreadsheetId, "QCode-Cardinality!A:C", 2, 29, 3, "QCode-Cardinality.adoc")
#    writeSpecDoc(service, spreadsheetId, "Property-Usage!A:E", 2, 97, 5, "Property-Usage.adoc")
    writeSpecDoc(service, spreadsheetId, "Property-UsageWcolour!A:E", 2, 96, 5, "Property-Usage-colour.adoc")
    writeSpecDoc(service, spreadsheetId, "URI-Siblings!A:E", 2, 28, 5, "URI-Siblings.adoc")
    writeSpecDoc(service, spreadsheetId, "CV-Usage!A:D", 2, 42, 4, "CV-Usage.adoc")
    writeSpecDoc(service, spreadsheetId, "CV-Usage-Key!A:B", 2, 10, 2, "CV-Usage-Key.adoc")
    writeSpecDoc(service, spreadsheetId, "Contact!A:D", 2, 10, 4, "Contact.adoc")
    writeSpecDoc(service, spreadsheetId, "Cardinality!A:C", 2, 29, 3, "Cardinality.adoc")
    writeSpecDoc(service, spreadsheetId, "Provider-CVs!A:C", 2, 43, 3, "Provider-CVs.adoc")
    writeSpecDoc(service, spreadsheetId, "IPTC7901!A:C", 2, 10, 3, "IPTC7901.adoc")
    writeSpecDoc(service, spreadsheetId, "NITF-head!A:C", 2, 10, 3, "NITF-head.adoc")
    writeSpecDoc(service, spreadsheetId, "NITF-docdata!A:C", 2, 16, 3, "NITF-docdata.adoc")
    writeSpecDoc(service, spreadsheetId, "NITF-body-head!A:C", 2, 11, 3, "NITF-body-head.adoc")
    writeSpecDoc(service, spreadsheetId, "IPTC7901-posttext!A:C", 2, 7, 3, "IPTC7901-posttext.adoc")
    writeSpecDoc(service, spreadsheetId, "RightsInfo-scope!A:B", 2, 5, 2, "RightsInfo-scope.adoc")
    writeSpecDoc(service, spreadsheetId, "RightsInfo-aspect!A:B", 2, 6, 2, "RightsInfo-aspect.adoc")
    writeSpecDoc(service, spreadsheetId, "HasInstrument!A:E", 2, 11, 5, "HasInstrument.adoc")
    writeSpecDoc(service, spreadsheetId, "Assert-Edit-Attributes!A:B", 2, 7, 2, "Assert-Edit-Attributes.adoc")
    writeSpecDoc(service, spreadsheetId, "Assert-i18n-Attributes!A:B", 2, 5, 2, "Assert-i18n-Attributes.adoc")
    writeSpecDoc(service, spreadsheetId, "Common-Power!A:E", 2, 10, 5, "Common-Power.adoc")
    writeSpecDoc(service, spreadsheetId, "Quantify-Attributes!A:C", 2, 5, 3, "Quantify-Attributes.adoc")
    writeSpecDoc(service, spreadsheetId, "Hint-Points!A:C", 2, 9, 3, "Hint-Points.adoc")
    writeSpecDoc(service, spreadsheetId, "Hint-Properties!A:E", 2, 37, 5, "Hint-Properties.adoc")
    writeSpecDoc(service, spreadsheetId, "Extension-Props!A:C", 2, 14, 3, "Extension-Props.adoc")
    writeSpecDoc(service, spreadsheetId, "Item-Relationship!A:C", 2, 13, 3, "Item-Relationship.adoc")
    writeSpecDoc(service, spreadsheetId, "Signal!A:C", 2, 5, 3, "Signal.adoc")
    writeSpecDoc(service, spreadsheetId, "Content-Warning!A:B", 2, 8, 2, "Content-Warning.adoc")
    writeSpecDoc(service, spreadsheetId, "User-Action!A:C", 2, 8, 3, "User-Action.adoc")
    writeSpecDoc(service, spreadsheetId, "Content-Rating!A:E", 2, 11, 5, "Content-Rating.adoc")
    writeSpecDoc(service, spreadsheetId, "Rating-Calc!A:C", 2, 9, 3, "Rating-Calc.adoc")
    writeSpecDoc(service, spreadsheetId, "Rating-Scale!A:C", 2, 5, 3, "Rating-Scale.adoc")
    writeSpecDoc(service, spreadsheetId, "Rater-Type!A:C", 3, 7, 3, "Rater-Type.adoc")
    writeSpecDoc(service, spreadsheetId, "Workflow-Actors!A:C", 2, 18, 3, "Workflow-Actors.adoc")
    writeSpecDoc(service, spreadsheetId, "Inline-Data!A:B", 2, 7, 2, "Inline-Data.adoc")
    writeSpecDoc(service, spreadsheetId, "Info-Source!A:C", 2, 8, 3, "Info-Source.adoc")
    writeSpecDoc(service, spreadsheetId, "Hop-Action!A:B", 2, 6, 2, "Hop-Action.adoc")
    writeSpecDoc(service, spreadsheetId, "HopAction-Target!A:B", 2, 5, 2, "HopAction-Target.adoc")
    writeSpecDoc(service, spreadsheetId, "incomingFeedId!A:B", 2, 5, 2, "incomingFeedId.adoc")
    writeSpecDoc(service, spreadsheetId, "origRep!A:C", 2, 7, 3, "origRep.adoc")
    writeSpecDoc(service, spreadsheetId, "Hash-Valuetype!A:B", 2, 6, 2, "Hash-Valuetype.adoc")
    writeSpecDoc(service, spreadsheetId, "Hash-Scope!A:B", 2, 5, 2, "Hash-Scope.adoc")
    writeSpecDoc(service, spreadsheetId, "Descriptive-Meta!A:C", 2, 9, 3, "Descriptive-Meta.adoc")
    writeSpecDoc(service, spreadsheetId, "Dimension-Default!A:C", 2, 7, 3, "Dimension-Default.adoc")
    writeSpecDoc(service, spreadsheetId, "Layout-Orient!A:B", 2, 7, 2, "Layout-Orient.adoc")
    writeSpecDoc(service, spreadsheetId, "Video-Scale!A:B", 2, 9, 2, "Video-Scale.adoc")
    writeSpecDoc(service, spreadsheetId, "Address!A:D", 2, 9, 4, "Address.adoc")
    writeSpecDoc(service, spreadsheetId, "Position!A:D", 2, 11, 4, "Position.adoc")
    writeSpecDoc(service, spreadsheetId, "Catalog!A:D", 2, 9, 4, "Catalog.adoc")
    writeSpecDoc(service, spreadsheetId, "KI-Updates!A:C", 2, 7, 3, "KI-Updates.adoc")
    writeSpecDoc(service, spreadsheetId, "QCode-Rules!A:B", 2, 6, 2, "QCode-Rules.adoc")
    writeSpecDoc(service, spreadsheetId, "Event-Description!A:D", 2, 7, 4, "Event-Description.adoc")
    writeSpecDoc(service, spreadsheetId, "Event-Relationships!A:C", 2, 7, 3, "Event-Relationships.adoc")
    writeSpecDoc(service, spreadsheetId, "Date-Values!A:C", 2, 7, 3, "Date-Values.adoc")
    writeSpecDoc(service, spreadsheetId, "Message-Attributes!A:D", 2, 8, 4, "Message-Attributes.adoc")
    writeSpecDoc(service, spreadsheetId, "Media-Type-Var!A:G", 2, 8, 7, "Media-Type-Var.adoc")
    writeSpecDoc(service, spreadsheetId, "Event-Conf!A:C", 2, 6, 3, "Event-Conf.adoc")





if __name__ == '__main__':
    main()
