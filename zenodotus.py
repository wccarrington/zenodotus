#! /usr/bin/env python3

import hashlib
import sys
import os
import time


def hashfile(filename):
    f = open(filename, 'rb')
    sha = hashlib.new('sha256')
    sha.update(f.read())
    return sha.hexdigest()


def escape_string(string):
    return '\\ '.join(string.split(' '))


# An index is a directory, with a store file, and one or more tag files
# the store file has lines of form "[sha256 hash] [file name]"
# the tag file's name is the tag, and have a list of hashes that have that tag
class Index:
    STORE_FILENAME = 'storefile'
    HISTORY_FILENAME = 'history'
    def __init__(self, dirname):
        self.dirname = dirname
        self.readindex()

    def readindex(self):
        self.files = {}
        self.hashes = {}
        self.tags = {}
        self.history = []
        infile = open(self.dirname + os.sep + self.STORE_FILENAME)
        for line in infile:
            shahash, filename = (l.strip() for l in line.split(None, 1))
            self.insert_file_with_hash(shahash, filename)
        for tagfile in os.listdir(self.dirname):
            if tagfile != self.STORE_FILENAME:
                self.tags[tagfile] = [l.strip() for l in open(os.path.join(self.dirname, tagfile)).readlines()]

    def writeindex(self):
        outfile = open(os.path.join(self.dirname, self.STORE_FILENAME), 'w')
        for filename, shahash in self.files.items():
            outfile.write(shahash + ' ' + filename + '\n')
        outfile.close()
        for tag, hashes in self.tags.items():
            if len(hashes) > 0:
                outfile = open(os.path.join(self.dirname, tag), 'w')
                for filehash in hashes:
                    outfile.write(filehash + '\n')
                outfile.close()
            else:
                os.remove(os.path.join(self.dirname, tag))
        outfile = open(os.path.join(self.dirname, self.HISTORY_FILENAME), 'a')
        for line in self.history:
            outfile.write(line + '\n')

    def insert(self, filename):
        shahash = hashfile(filename)
        self.insert_file_with_hash(shahash, filename)
        self.history.append('INSERT %i %s %s' % (time.time(), shahash, escape_string(filename)))

    def insert_file_with_hash(self, shahash, filename):
        self.files[filename] = shahash
        self.hashes[shahash] = filename

    def dump(self):
        for filename, shahash in self.files.items():
            print(filename, shahash)
            for tag, filehashes in self.tags.items():
                if shahash in filehashes:
                    print(tag)
            print()

    def dumptag(self, tag):
        for filehash in self.tags[tag]:
            print(self.hashes[filehash])

    def maketag(self, tag):
        if tag not in self.tags:
            self.tags[tag] = []

    def addtag(self, filename, tag):
        if filename in self.files:
            self.maketag(tag)
            self.tags[tag].append(self.files[filename])
            self.history.append('ADDTAG %i %s %s' % (time.time(), escape_string(tag), escape_string(filename)))


def main():
    if len(sys.argv) < 2:
        print('Must supply an argument')
        return
    if sys.argv[1] == 'insert':
        filename = sys.argv[2]
        filename = os.path.abspath(filename)
        print('Inserting file:', filename)
        index = Index('zenoindex')
        index.insert(filename)
        index.writeindex()
    elif sys.argv[1] == 'dump':
        index = Index('zenoindex')
        index.dump()
    elif sys.argv[1] == 'dumptag':
        tagname = sys.argv[2]
        index = Index('zenoindex')
        index.dumptag(tagname)
    elif sys.argv[1] == 'addtag':
        filename = sys.argv[2]
        filename = os.path.abspath(filename)
        tagname = sys.argv[3]
        index = Index('zenoindex')
        index.addtag(filename, tagname)
        index.writeindex()
    else:
        print('Unknown option:', sys.argv[1])


if __name__ == '__main__':
    main()
