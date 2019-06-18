import vtk, qt, ctk, slicer, PythonQt


# ICON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/Resources/Icons/'

#
# Home
#

class Home:
    def __init__(self, parent):
        parent.title = "Home"
        parent.categories = ["Shape Analysis Toolbox"]
        parent.dependencies = []
        parent.contributors = ["Kitware, Inc., The University of North Carolina at Chapel Hill, and NYU Tandon School of Engineering"]
        parent.helpText = """<center>
        <br>
        <b>Welcome to SlicerSALT!</b><br>
        <br>
        Visit <a href="https://salt.slicer.org">salt.slicer.org</a> for more information about SlicerSALT.<br>
        <br>
        Documentation and tutorials can be found at: <a href="https://salt.slicer.org/docs/">salt.slicer.org/docs/</a><br>
        </center>
        """
        parent.acknowledgementText = """
        <center> <br>SlicerSALT is an open source software package for doing shape analysis of image segmentations using different methods. <br>
        <br> Ongoing development, maintenance, distribution, and training is managed by UNC Chapel Hill, NYU Tandon School of Engineering and Kitware Inc.<br>
        <br> The project is funded by NIH grant: NIBIB R01EB021391 (Paniagua B). <br>
        <br> SlicerSALT is supported by NIH and the Slicer Community. <br>
        </center>
        """

        # parent.icon = qt.QIcon("%s/cranioIcon.png" % ICON_DIR)

        self.parent = parent


#
# qHomeWidget
#

class HomeWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    def setup(self):

        # TEXT
        text = """
<br>
<u>Workflow quick-reference:</u><br>
<br>
The drop-down Modules are ordered to follow the basic workflow for choosing and using data.  As a quick reference, the basic steps involve:<br>
<br>
&nbsp; 1. Use the <a href="#"><b>Data importer</b></a> module to load your segmentations from FreeSurf, FSL, Autoseg, or a bunch of vtp's<br><br>
&nbsp; 2. Use <a href="#"><b>Shape Population Viewer</b></a> to do a quality check on the imported data<br><br>
&nbsp; 3. Use <a href="#"><b>SPHARM Shape Analysis Module</b></a> to do spherical harmonics based analysis<br><br>
&nbsp; 4. Use the <a href="#"><b>Study-specific Shape Analysis</b></a> module.<br><br>
&nbsp; 5. Use the <a href="#"><b>S-Rep Shape Analysis</b></a> module to do shape analysis via skeletal representations.<br><br>
&nbsp; 6. Use the <a href="#"><b>Shape Evaluator</b></a> module to compute a mean shape and see how the population varies.<br><br>
&nbsp; 7. Use <a href="#"><b>Shape Regressions</b></a> module to do regression based analysis.<br><br>
&nbsp; 8. Use the <a href="#"><b>Shape Statistics</b></a> module.<br><br>
"""

        # TEXTEDIT
        self.HomeTextSection = qt.QTextEdit()
        self.HomeTextSection.setReadOnly(True)
        self.HomeTextSection.setText(text)
        self.HomeTextSection.setMinimumHeight(400)
        self.HomeTextSection.connect('cursorPositionChanged()', self.slot)
        self.layout.addWidget(self.HomeTextSection)

        # SPACER
        self.layout.addStretch()


        #SAMPLE DATA REGISTRATION
        json_list = [self.resourcePath('SampleDataDescription/ShapeRegressionInputData.json'),
                     self.resourcePath('SampleDataDescription/DataImporterInputData.json'),
                     self.resourcePath('SampleDataDescription/SPHARM-PDMTestData.json'),]

        for json_file in json_list:
            with open(json_file, 'r') as f:
                source_data = json.load(f)
                #Register sample datasets for each module
                iconPath = os.path.join(os.path.dirname(__file__).replace('\\','/'), 'Resources','Icons')
                iconPath = None
                #Data Importer sample dataset registration
                SampleData.SampleDataLogic.registerCustomSampleDataSource(
                  category=source_data['category'], sampleName=source_data['sampleName'],
                  uris=source_data['uris'],
                  fileNames=source_data['fileNames'],
                  nodeNames=None,
                  thumbnailFileName=iconPath,
                  loadFileType=None,
                  customDownloader = self.DownloadSampleDataInFolder,
                  checksums = source_data['checksums']
                )

    def slot(self):
        pos = self.HomeTextSection.textCursor().position()

        if pos >= 181 and pos <= 194 :
            slicer.util.selectModule(slicer.moduleNames.DataImporter)
        elif pos >= 288 and pos <= 311 :
            slicer.util.selectModule(slicer.moduleNames.ShapePopulationViewer)
        elif pos >= 365 and pos <= 393 :
            slicer.util.selectModule(slicer.moduleNames.ShapeAnalysisModule)
        elif pos >= 449 and pos <= 478 :
            slicer.util.selectModule(slicer.moduleNames.GroupWiseRegistrationModule)
        elif pos >= 501 and pos <= 522 :
            slicer.util.selectModule(slicer.moduleNames.SkeletalRepresentationVisualizer)
        elif pos >= 594 and pos <= 610 :
            slicer.util.selectModule(slicer.moduleNames.Home) #SVA
        elif pos >= 686 and pos <= 703 :
            slicer.util.selectModule(slicer.moduleNames.RegressionComputation)
        elif pos >= 758 and pos <= 774 :
             slicer.util.selectModule(slicer.moduleNames.Home) #MFSDA


    def DownloadSampleDataInFolder(self,source):
        print(self)
        destFolderPath = str(qt.QFileDialog.getExistingDirectory())

        if not os.path.isdir(destFolderPath):
            print('Invalid path %s' %{destFolderPath})
            print("Can't download the sample data")
            return

        if not hasattr(source,'checksums'):
            checksums = [None] * len(source.uris)
        else:
            checksums = source.checksums

        for uri, fileName, checksum  in zip(source.uris,source.fileNames,checksums):
            self.downloadFile(uri, destFolderPath, fileName, checksum=checksum)

        print('Data folder: %s' % destFolderPath)

    def reportHook(self,blocksSoFar,blockSize,totalSize):
        # we clamp to 100% because the blockSize might be larger than the file itself
        percent = min(int((100. * blocksSoFar * blockSize) / totalSize), 100)
        if percent == 100 or (percent - self.downloadPercent >= 10):
          # we clamp to totalSize when blockSize is larger than totalSize
          humanSizeSoFar = self.humanFormatSize(min(blocksSoFar * blockSize, totalSize))
          humanSizeTotal = self.humanFormatSize(totalSize)
          print('<i>Downloaded %s (%d%% of %s)...</i>' % (humanSizeSoFar, percent, humanSizeTotal))
          self.downloadPercent = percent

    def downloadFile(self, uri, destFolderPath, name, checksum=None):
        """
        :param uri: Download URL.
        :param destFolderPath: Folder to download the file into.
        :param name: File name that will be downloaded.
        :param checksum: Checksum formatted as ``<algo>:<digest>`` to verify the downloaded file. For example, ``SHA256:cc211f0dfd9a05ca3841ce1141b292898b2dd2d3f08286affadf823a7e58df93``.
        """
        filePath = destFolderPath + '/' + name
        (algo, digest) = extractAlgoAndDigest(checksum)
        if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
          import urllib.request, urllib.parse, urllib.error
          print('<b>Requesting download</b> <i>%s</i> from %s ...' % (name, uri))
          # add a progress bar
          self.downloadPercent = 0
          try:
            urllib.request.urlretrieve(uri, filePath, self.reportHook)
            print('<b>Download finished</b>')
          except IOError as e:
            print('<b>\tDownload failed: %s</b>' % e, logging.ERROR)

          if algo is not None:
            print('<b>Verifying checksum</b>')
            current_digest = computeChecksum(algo, filePath)
            if current_digest != digest:
              print('<b>Checksum verification failed. Computed checksum %s different from expected checksum %s</b>' % (current_digest, digest))
              qt.QFile(filePath).remove()
            else:
              print('<b>Checksum OK</b>')
        else:
          if algo is not None:
            print('<b>Verifying checksum</b>')
            current_digest = computeChecksum(algo, filePath)
            if current_digest != digest:
              print('<b>File already exists in cache but checksum is different - re-downloading it.</b>')
              qt.QFile(filePath).remove()
              return self.downloadFile(uri, destFolderPath, name, checksum)
            else:
              print('<b>File already exists and checksum is OK - reusing it.</b>')
          else:
            print('<b>File already exists in cache - reusing it.</b>')
        return filePath

    def humanFormatSize(self,size):
        """ from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size"""
        for x in ['bytes','KB','MB','GB']:
          if size < 1024.0 and size > -1024.0:
            return "%3.1f %s" % (size, x)
          size /= 1024.0
        return "%3.1f %s" % (size, 'TB')
