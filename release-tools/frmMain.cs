/*****************************************************************************
Company: IPTC - International Press Telecommunications Council - www.iptc.org
Copyright: 2007 IPTC, All rights reserved
Author: Michael W Steidl
 
VS 2005 Solution: SimpleTools1
Project: CancelDocVersInXsd

StartDate: 2007-10-18
******************************************************************************/
using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.IO;
using System.Windows.Forms;

namespace CancelDocVersInXsd
{
    public partial class frmMain : Form
    {
        private const string PgmVersion = "1.1";
        /* Version history: (latest entry on top)
         * 
		 * 2007-10-24 1.1 mws: inserting the XML declaration added
         * 2007-10-18 1.0 mws: initial version
         */

        private string sXsdFolderName;

        public frmMain()
        {
            InitializeComponent();
            sXsdFolderName = string.Empty;
            tslblXsdFolder.Text = sXsdFolderName;
			Text += " " + PgmVersion;

        }

        //***************************************************************************
        public void AddToLog(string sLogLine)
        {
            string sW = String.Format("{0:yyyy-MM-dd HH:mm:ss}", DateTime.Now) + ": " +
                sLogLine;
            listBoxLogging.Items.Insert(0, sW);
            // trim at end if the log is getting to long
            if (listBoxLogging.Items.Count > 10000)
            {
                for (int iIdx = listBoxLogging.Items.Count - 1; iIdx > 5000; iIdx--)
                {
                    listBoxLogging.Items.RemoveAt(iIdx);
                }
            }
            listBoxLogging.Update();
        }

        //***************************************************************************
        private void ProcessXsdFiles()
        // Code History:
        // 2007-10-18  mws
        {
            StringCollection scXsdFilenames = new StringCollection();

            string sW;
            string sOldFn, sNewFn;
            string sSaveLine;
            int iPosUsc, iPosDot;
            int iW;

            DirectoryInfo diLocal = new DirectoryInfo(sXsdFolderName);
            FileInfo[] fiResult = diLocal.GetFiles("*.xsd");
            foreach (FileInfo fiT in fiResult)
            {
                // Delete the doc version in the file name
                sOldFn = fiT.FullName;
                iW = fiT.DirectoryName.Length + 1;
                sSaveLine = sOldFn.Substring(iW) + "|"; // save only the file name, not the path
                iPosUsc = sOldFn.LastIndexOf('_');
                if (iPosUsc > -1)
                {
                    iPosDot = sOldFn.LastIndexOf('.');
                    if ((iPosDot > -1) & (iPosDot > iPosUsc))
                    {
                        sNewFn = sOldFn.Remove(iPosUsc, iPosDot - iPosUsc);
                        sSaveLine += sNewFn.Substring(iW); // save only the file name, not the path

                        // Ensure that the target does not exist.
                        if (File.Exists(sNewFn))
                            File.Delete(sNewFn);

                        // Move = rename the file.
                        try
                        {
                            File.Move(sOldFn, sNewFn);
                        }
                        catch { continue; }

                        scXsdFilenames.Add(sSaveLine);
                        AddToLog("File renamed: " + sOldFn);

                    }
                }
            } // foreach
            // now once again: update the XML content of the xsd files
            string sXML;
            string[] saFNames;
			bool bWriteFile;
            fiResult = diLocal.GetFiles("*.xsd");
            foreach (FileInfo fiT in fiResult)
            {
                if (ReadTextFromFile(fiT.FullName, out sXML, "utf-8"))
                {
					bWriteFile = false;
					if ((sXML.IndexOf("<?xml") < 0) | (sXML.IndexOf("<?xml") > 10))
					{
						sXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n" + sXML;
						bWriteFile = true;
					}
                    foreach (string sT in scXsdFilenames)
                    {
                        saFNames = sT.Split('|');
                        if (saFNames.Length == 2)
                        {
                            if (sXML.IndexOf(saFNames[0]) > -1)
                            {
                                sXML = sXML.Replace(saFNames[0], saFNames[1]);
								bWriteFile = true;
                            }
                        }
                    } // foreach XsdFilename

					if (bWriteFile)
					{
						WriteTextToFile(sXML, fiT.FullName, "utf-8", false);
						AddToLog("XML in file processed: " + fiT.FullName);
					}

                } // if successful read
            } // foreach fiResult

        } // ProcessXsdFiles


        private void SelectXsdFolder()
            // Code History:
            // 2007-10-18 mws
        {
            fbdgXsdFiles.ShowDialog();
            sXsdFolderName = fbdgXsdFiles.SelectedPath;
            tslblXsdFolder.Text = sXsdFolderName;
            Update();
        } // SelectXsdFolder

        //********************************************************************************
        #region ***** T E X T F I L E   UTILITIES
        //***** T E X T F I L E  UTILITIES ***********************************************

        //***************************************************************************
        private bool WriteTextToFile(
            string sText,
            string sFilename,
            string sEncoding,
            bool bAppend)
        // Code History:
        // 2007-10-03 mws
        {
            StreamWriter swText = null;
            try
            {
                swText = new StreamWriter(sFilename, bAppend, Encoding.GetEncoding(sEncoding));
            }
            catch { return false; }
            try
            {
                swText.Write(sText);
                swText.Close();
            }
            catch { return false; }

            return true;
        } // WriteTextToFile

        //***************************************************************************
        /// <summary>
        /// Reads the content of a text file into a string
        /// </summary>
        /// <param name="sFilename">Name of the file</param>
        /// <param name="sText">Returned text from the file</param>
        /// <param name="sEncoding">"Magic word" for the encoding, if empty: NET/Windows probing</param>
        /// <returns>Success of text retrieval from the file</returns>
        private bool ReadTextFromFile(string sFilename, out string sText, string sEncoding)
        // Code History:
        // 2007-10-03 mws
        {
            sText = string.Empty;

            if (!File.Exists(sFilename))
                return false;

            StreamReader srText = null;
            try
            {
                if (string.IsNullOrEmpty(sEncoding))
                    srText = new StreamReader(sFilename, true);
                else
                    srText = new StreamReader(sFilename, Encoding.GetEncoding(sEncoding));
            }
            catch { return false; }
            try
            {
                sText = srText.ReadToEnd();
                srText.Close();
            }
            catch { return false; }
            return true;
        } // ReadTextFromFile

        //**************************************************************************
        // ***** AUTOCREATED
        //**************************************************************************

        private void selectXSDFolderToolStripMenuItem_Click(object sender, EventArgs e)
        {
            SelectXsdFolder();
        } 


        #endregion

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Close();
        }

        private void toolStripButton1_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(sXsdFolderName))
                SelectXsdFolder();

            if (!string.IsNullOrEmpty(sXsdFolderName))
                ProcessXsdFiles();

        }

    }
}