__author__ = 'PoojaNihalani'

import csv
import sys
import getopt

header_map = {
  'Sku':'id',
  'ProductName':'title',
  'ProductDescription':'description',
  'Category':'google_product_category',
  'ProductType':'product_type',
  'ProductURL':'link',
  'ImageURL':'image_link',
  'Manufacturer/Brand':'brand',
  'MSRPPrice':'price',
  'CurrentPrice':'sale_price',
  'StockStatus':'availability',
  'Color':'color',
  'Gender':'gender',
  'Size':'size',
  'AgeGroup':'age_group',
  'Condition':'condition'
}

def map_header(header, header_map):
  new_header = []
  for each in header:
    if each in header_map:
      new_header.append(header_map[each])
    else:
      new_header.append(each)
  return new_header

def convert(input_file, output_file, delimiter="\t"):
  with open(input_file, 'rb') as infile:
      with open(output_file, 'w') as outfile:
          reader = csv.reader(infile, dialect='excel', delimiter='\t')
          writer = csv.writer(outfile, dialect='excel', delimiter='\t')
          is_header = True
          #write new header


          for row in reader:
            if is_header:
              new_header = map_header(row, header_map)
              row = map_header(new_header, header_map)
            writer.writerow(row)
            #print row



if __name__ == '__main__':
  input_file = ''
  output_file = ''
  argv = sys.argv[1:]
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    print 'kirkland_format_file.py -i <inputfile> -o <outputfile>'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      input_file = arg
    elif opt in ("-o", "--ofile"):
      output_file = arg
  print 'Input file is "', input_file
  print 'Output file is "', output_file
  convert(input_file, output_file)

#convert(input_file="/Users/PoojaNihalani/Downloads/kirklands_20151027.txt",output_file="/Users/PoojaNihalani/Downloads/kirklands_modified.csv")