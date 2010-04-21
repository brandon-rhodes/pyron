"""Routines for building tar.gz source distributions."""

import os
import tarfile

# NOTE: this module is incomplete; it represents only the first halting
# steps to create the ability to write sdist archives from Pyron, work
# which stalled when I realized how hard it was going to be to write all
# of the little rules to try to induce a "setup.py" file to install
# exactly the right combination of Python files, other files, and entry
# points for a particular project.

def write_sdist(project, outfile):
    """Write a tarfile sdist for `project` to the stream `outfile`."""
    tar = tarfile.open(mode='w:gz', fileobj=outfile)
    for path in project.find_files():
        print path, os.path.relpath(path, project.dir)
    tar.close()

def save_temporary_sdist(project, tmpdir):
    """Create a temporary .tar.gz file and save a tarfile into it."""
    filename = '%s-%s.tar.gz' % (project.name, project.version)
    filepath = os.path.join(tmpdir, filename)
    outfile = open(filepath, 'w')
    write_sdist(project, outfile)
    outfile.close()
    return filepath
