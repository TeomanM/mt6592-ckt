#!/usr/bin/python2.6

import xml.dom.minidom as xdom
from optparse import OptionParser
import shutil
import sys
import os
import re

parser = OptionParser(usage="usage: %prog [options] TrunkSrc BSPDest BSPMovingRulesXml",version="%prog 1.0")
(options,args) = parser.parse_args()
if len(args) != 3:
    parser.print_help()
    sys.exit(1)

class Arguments(object):pass
ARGUMENTS = Arguments()
ARGUMENTS.trunkSrc = os.path.abspath(args[0])
ARGUMENTS.bspDest = os.path.abspath(args[1])
ARGUMENTS.xml = os.path.abspath(args[2])

# check the arguments correctness
def checkArgument(arg):
    """ check the argument """
    if not os.path.exists(arg.trunkSrc):
        print("the input TrunkSrc '%s' does not exist!" % arg.trunkSrc, file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(arg.bspDest):
        print("the input BSPDest '%s' does not exist!" % arg.bspDest, file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(arg.xml):
        print("the input xml '%s' does not exist!" % arg.xml, file=sys.stderr)
        sys.exit(1)

checkArgument(ARGUMENTS)

# define our own  XML-DOM class for BSP moving rules
class XmlDom(object):
    def __init__(self,xml):
        self.xmlDom = xdom.parse(xml)

    def getRoot(self):
        return self.xmlDom.documentElement

    def getMovingDirList(self):
        root = self.getRoot()
        dirElement = root.getElementsByTagName("DirList")[0].getElementsByTagName("MoveDirList")[0].getElementsByTagName("Dir")
        dirList = list(map(str,[item.firstChild.nodeValue for item in dirElement if item.firstChild is not None]))
        return dirList

    def getRemovingDirList(self):
        root = self.getRoot()
        dirElement = root.getElementsByTagName("DirList")[0].getElementsByTagName("DeleteDirList")[0].getElementsByTagName("Dir")
        dirList = list(map(str,[item.firstChild.nodeValue for item in dirElement if item.firstChild is not None]))
        return dirList

    def getMovingFileList(self):
        root = self.getRoot()
        fileElement = root.getElementsByTagName("FileList")[0].getElementsByTagName("MoveFileList")[0].getElementsByTagName("File")
        fileList = list(map(str,[item.firstChild.nodeValue for item in fileElement if item.firstChild is not None]))
        return fileList

    def getRemovingFileList(self):
        root = self.getRoot()
        fileElement = root.getElementsByTagName("FileList")[0].getElementsByTagName("DeleteFileList")[0].getElementsByTagName("File")
        fileList = list(map(str,[item.firstChild.nodeValue for item in fileElement if item.firstChild is not None]))
        return fileList

#end XmlDom

# create DOM of BSP moving rules
dom = XmlDom(ARGUMENTS.xml)

###################################################
#    all class definitions of the Dir/File Type
###################################################

class DirElement(object):
    def __init__(self):
        """ dir release initialization """
        self.mdirs = dom.getMovingDirList()
        self.rdirs = dom.getRemovingDirList()
        self.src = ARGUMENTS.trunkSrc
        self.dest = ARGUMENTS.bspDest

    def sourceMoving(self):
        for d in self.mdirs:
            sourceDir = os.path.join(self.src,d)
            destinationDir = os.path.join(self.dest,d)
            if not os.path.exists(sourceDir):
                print("Error!Dir: Moving Source Directory '%s' does not exists!" % sourceDir, file=sys.stderr)
                sys.exit(2)
            if not os.path.isdir(sourceDir):
                print("Error!Dir: %s in DirList is not a directory, check your moving rules!" % sourceDir, file=sys.stderr)
                sys.exit(2)
            print("Dir Moving:copy %s ..." % sourceDir, file=sys.stdout)
            if not os.path.exists(destinationDir):
                os.makedirs(destinationDir)
            os.system("rsync -a --delete --force %s/ %s" % (sourceDir,destinationDir))

    def destinationRemoving(self):
        for d in self.rdirs:
            destinationDir = os.path.join(self.dest,d)
            print("Dir Removing:delete %s ..." % destinationDir, file=sys.stdout)
            os.system("rm -rf %s" % destinationDir)

    def go(self):
        self.sourceMoving()
        self.destinationRemoving()

# end DirElement

class FileElement(object):
    def __init__(self):
        """ file release initialization """    
        self.mfiles = dom.getMovingFileList()
        self.dfiles = dom.getRemovingFileList()
        self.src = ARGUMENTS.trunkSrc
        self.dest = ARGUMENTS.bspDest

    def sourceMoving(self):
        for f in self.mfiles:
            sourceFile = os.path.join(self.src,f)
            destinationFile = os.path.join(self.dest,f)
            if not os.path.exists(sourceFile):
                print("Error!File: Release Source File '%s' does not exists!" % sourceFile, file=sys.stderr)
                sys.exit(3)
            if not os.path.isfile(sourceFile):
                print("Error!File: %s in FileList is not a file, check your moving rules!" % sourceFile, file=sys.stderr)
                sys.exit(3)
            dirPath = os.path.dirname(destinationFile)
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            print("File Moving:copy %s ..." % sourceFile, file=sys.stdout)
            os.system("rsync -a %s %s" % (sourceFile,destinationFile))

    def destinationRemoving(self):
        for d in self.dfiles:
            destinationFile = os.path.join(self.dest,d)
            print("File Removing:delete %s ..." % destinationFile, file=sys.stdout)
            os.system("rm -f %s" % destinationFile)

    def go(self):
        self.sourceMoving()
        self.destinationRemoving()

# end FileElement

###############################################
#            begin to transfer
###############################################

def main():
    """ mediatek custom release """
    # initialzation
    dirs = DirElement()
    files = FileElement()
    # moving/removing steps
    dirs.go()
    files.go()
    print("BSP transfering[done]!", file=sys.stdout)

# end main

main()
