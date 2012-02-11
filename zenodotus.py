#! /usr/bin/env python3

import hashlib
import sys


def hashfile(filename):
    f = open(filename, 'rb')
    sha = hashlib.new('sha256')
    sha.update(f.read())
    return sha.hexdigest()


class Index:
    def __init__(self, filename):
        self.filename = filename
        self.readindex()

    def readindex(self):
        self.files = {}
        self.hashes = {}
        infile = open(self.filename)
        for line in infile:
            shahash, filename = (l.strip() for l in line.split(None, 1))
            self.insert_file_with_hash(shahash, filename)

    def writeindex(self):
        outfile = open(self.filename, 'w')
        for filename, shahash in self.files.items():
            outfile.write(shahash + ' ' + filename + '\n')
        outfile.close()

    def insert(self, filename):
        shahash =  hashfile(filename)
        self.files[filename] = shahash
        self.hashes[shahash] = filename

    def insert_file_with_hash(self, shahash, filename):
        self.files[filename] = shahash
        self.hashes[shahash] = filename


def main():
    if sys.argv[1] == 'insert':
        filename = sys.argv[2]
        index = Index('index.zeno')
        index.insert(filename)
        index.writeindex()


if __name__ == '__main__':
    main()
