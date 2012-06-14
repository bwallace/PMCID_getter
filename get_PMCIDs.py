import Bio
from Bio import Medline
from Bio import Entrez
import sys
import pdb
import optparse

# tell Entrez who I am.
Entrez.email = "byron.wallace@gmail.com"


def get_pmcid(title=None, pmid=None):
    if title is None and pmid is None:
        print "you need to provide either a title or a PMID!"
        return False

    if pmid is None:
        pmid = get_pmid_from_title(title)
        if not pmid:
            # then we couldn't find a pubmed id for this guy.
            return "no PMID found"

    record = get_record_from_pmid(pmid)
    print "retrieved citation '{0}'".format(record["TI"])
    return get_pmcid_from_record(record)

def get_pmid_from_title(title):
    handle = Entrez.esearch(db="pubmed",
                term='{0}'.format(title),
                field="titl")

    # what did we get?
    records = Entrez.read(handle)
    id_list = records["IdList"]
    # one? more than one?
    num_records = len(id_list)
    if num_records == 0:
        print "no records found for '{0}'".format(title)
        return False
    elif len(id_list) > 1:
        print "warning -- I retrieved more than 1 citation for '{0}'; I'm going to use the first.".\
                    format(title)
    

    return id_list[0]

def get_record_from_pmid(pmid):
    # now get the actual citation; should really only be a singleton,
    # but this library likes to operate over lists
    citations = Entrez.efetch(db="pubmed",id=pmid,
                                rettype="medline",retmode="text")

    # again, Bio likes to operate on lists, even though we only have
    # a singleton here
    record = list(Medline.parse(citations))[0]
    return record

def get_pmcid_from_record(record):
    ''' extract the PMCID from the record (... if it exists) '''

    # do we have a PMCID? 
    if record.has_key("PMC"):
        print "ok -- found a PMCID for '{0}'".format(record["TI"])
        return record["PMC"]
    else:
        print "sorry, '{0}' doesn't have a PMCID".format(record["TI"])
        return "no PMCID found"

def looks_like_a_pmid(line):
    # quick and dirty -- I'm sure we could do better
    try:
        pmid = int(line)
        return True
    except:
        return False

def parse_input_file(input_file_path):
    tuples = [] # list of (title, pmcid) pairs
    with open(input_file_path) as f:
        for line in f.readlines():
            line = line.replace("\n", "").strip()
            if line != "":
                if looks_like_a_pmid(line):
                    pmcid = get_pmcid(pmid=line)
                else:
                    pmcid = get_pmcid(title=line)
                print "adding ({0}, {1})".format(line, pmcid)
                tuples.append((line, pmcid))

    return tuples
            

def write_out(ids_and_PMCIDs, out_path):
    # id_ can be either a PMID or title
    out_str = []
    for id_, PMCID in ids_and_PMCIDs:
        out_str.append("{0}\t{1}".format(id_, PMCID))

    with open(out_path, 'w') as fout:
        fout.write("\n".join(out_str))
        fout.close()

def main():
    parser = optparse.OptionParser(usage="PMCID getter -- please specify an input file")

    parser.add_option("-f", "--file",
                      action="store",
                      dest="file_path",
                      help="specify the input file path: this file should contain one title or PMID per line.")

    parser.add_option("-o", "--out_path",
                      action="store",
                      dest="out_path",
                      help="specify where the output should go.")

    (options, args) = parser.parse_args()

    # for now both args are required
    if options.out_path is None or options.file_path is None:
        print "you need to specify both an input file and an output path! try the -h option for help."
        return None

    tuples = parse_input_file(options.file_path)
    
    print "writing PMCIDs out to {0}".format(options.out_path)
    write_out(tuples, options.out_path)



if __name__ == "__main__":
    main()

