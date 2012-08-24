#!/usr/bin/python

import shutil
import re

# XXX: make this an context

class CFile:
    """
    Will write whatever you feed push_line(s) in the space between the
    deliminer string, formated with begin_id or end_id as begin_or_end
    and with generate_tag as tag.

    Also keeps backup according to argument backup_format (only format
    argument is the string filename).

    It is safe to delete this at any time. We keep no open files.

    Note1: The first occrance of deliminers will be used ONLY. Use
    different tags to edit different parts of the file separately.

    Note2: The lines containing deliminers are left untouched. Keeping
    them completely separate is suggested.

    Note3: any changes commited to the file between tha beginning and
    end of a CFile's lifetime will be overwritten
    """
    def __init__(self, filename, tag, readonly=False, deliminer_string = "/* %(begin_or_end)s generated code: %(tag)s */", begin_id = "Begin", end_id = "End", backup_format = "%s~"):
        """
        filename:     The filename to edit

        generate_tag: Each automatically editable region has a unique
                      tag that characterizes the control domain of
                      Cfile

        deliminer_string: This is a formatable string with parameters
                          begin_or_end to distinguish between start
                          and end deliminer and tag to distingush
                          between the regions of control of different
                          CFile objects

        begin_id: Substituted in deliminer_string to retrieve the
                  beginning of the control region

        end_id: Substituted in deliminer_string to retrieve the
                end of the control region

        backup_format: the format of the backup file that is
                       automatically kept. Set to None for no backup.
        """

        self.filename = filename
        self.readonly = readonly

        if not readonly:
            if backup_format:
                shutil.copy(filename, backup_format % filename)
            else:
                backup_format = "%s"

        # Break the file lines into lists
        self.top_list, self.mid_list, self.old_mid_list, self.bottom_list = [], [], [], []

        self.pattern = {'begin': deliminer_string % dict(begin_or_end=begin_id, tag=tag),
                        'end' : deliminer_string % dict(begin_or_end=end_id, tag=tag)}

        checkpoints = iter(['begin', 'end'])
        looking_for = next(checkpoints, None)

        with open(filename) as f:
            for i in f:
                # Before the region of interest
                if looking_for == 'begin':
                    self.top_list.append(i.rstrip())

                # In the region of interest
                if looking_for == 'end':
                    self.old_mid_list.append(i.rstrip())

                # Below the region of interest
                if looking_for is None:
                    self.bottom_list.append(i.rstrip())

                # Found what we were looking for
                if looking_for and self.pattern[looking_for] in i:
                    looking_for = next(checkpoints, None)

        if looking_for:
            raise Exception("Failed to find "+looking_for+" tag: "+self.pattern[looking_for])

        if self.readonly:
            self.mid_list = self.old_mid_list

    def push_line(self, string):
        """Push line to be written to the file. Nothing is written
        until flush is called. Lines should contain newline
        characters.
        """
        self.push_lines([string])

    def push_lines(self, lines):
        """Push a list of lines into the file."""
        if self.readonly:
            raise Exception("Tried to push line in readonly file %s" % self.filename)

        self.mid_list += lines

    def search(self, string):
        """Search the region. return the lines that contains the string."""
        return [l for l in self.old_mid_list if string in l]

    def contents(self, real=False):
        """Return the current contents of the region. If real is true
        then we get the contents of the file right now, if not we get
        what the file would have after flush. If the file is readonly
        real has no effect.
        """
        if real:
            return self.old_mid_list
        else:
            return self.mid_list

    def flush(self):
        """Flushing also closes the file. Has no effect if readonly is on."""
        if self.readonly:
            return

        with open(self.filename, 'w') as f:
            f.writelines( [str(i)+"\n" for i in self.top_list + self.mid_list + self.bottom_list] )
        self.old_mid_list = self.mid_list
        self.mid_list = []

if __name__ == "__main__":
    from sys import argv

    # Assuming scavenger-opc.h is in the current directory.
    # The only thing that would change for a verilog file would be the __init__ parameters:
    # f = Cfile('file.v', 'tag_name', '// some comment that contains %(begin_or_end)s and %(tag)s')

    from examples import opcode_gen

    f = CFile('scavenger-opc.h', 'OpcodeStruct')
    f.push_lines([str(i)+",\n" for i in opcode_gen.opcodeStructFactory('testtable.txt')])
    f.flush()
