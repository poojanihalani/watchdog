"""
  xml2csv.py
  Kailash Nadh, http://nadh.in
  October 2011

  License:        MIT License
  Documentation:    http://nadh.in/code/xmlutils.py
"""

import codecs
import re
import xml.etree.ElementTree as et

class xml2csv:

  def __init__(self, input_file, output_file, encoding='utf-8'):
    """Initialize the class with the paths to the input xml file
    and the output csv file

    Keyword arguments:
    input_file -- input xml filename
    output_file -- output csv filename
    encoding -- character encoding
    """
    self.header_map = {
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
    self.output_buffer = []
    self.output = None

    # open the xml file for iteration
    self.context = et.iterparse(input_file, events=("start", "end"))
    self.header_context = et.iterparse(input_file, events=("start", "end"))
    print self.context
    # output file handle
    try:
      self.output = codecs.open(output_file, "w", encoding=encoding)
    except:
      print("Failed to open the output file")
      raise

  def _get_header(self, tag="item", delimiter=",", ignore=[], noheader=False):
    """Get Headers in first pass"""
    started = False
    tagged =False
    header_line = []
    field_name = ''
    # iterate through the xml
    for event, elem in self.header_context:
      # if elem is an unignored child node of the record tag, it should be written to buffer
      should_write = elem.tag != tag and started and elem.tag not in ignore
      # and if a header is required and if there isn't one
      should_tag = not tagged and should_write and not noheader

      if event == 'start':
        if elem.tag == tag and not started:
          started = True
        elif should_tag:
          # if elem is nested inside a "parent", field name becomes parent_elem
          field_name = '_'.join((field_name, elem.tag)) if field_name else elem.tag
      else:
        if should_write and elem.tag not in header_line and should_tag:
          header_line.append(elem.tag)
    elem.clear()  # discard element and recover memory
    self.header_line = header_line
    print header_line

  def convert(self, tag="product", delimiter="\t", ignore=[], noheader=False,
        limit=-1, buffer_size=1000):

    """Convert the XML file to SQL file

      Keyword arguments:
      tag -- the record tag. eg: item
      delimiter -- csv field delimiter
      ignore -- list of tags to ignore
      limit -- maximum number of records to process
      buffer -- number of records to keep in buffer before writing to disk

      Returns:
      number of records converted,
    """

    # get to the root
    event, root = self.context.next()

    #header_line = []
    field_name = ''

    tagged = False
    started = False
    n = 0

    self._get_header(tag, delimiter, ignore, noheader)
    processed_fields = dict(zip(self.header_line, [" "]*len(self.header_line)))
    # iterate through the xml
    for event, elem in self.context:
      # if elem is an unignored child node of the record tag, it should be written to buffer
      should_write = elem.tag != tag and started and elem.tag not in ignore
      # and if a header is required and if there isn't one
      should_tag = not tagged and should_write and not noheader

      if event == 'start':
        if elem.tag == tag and not started:
          started = True
        elif should_tag:
          # if elem is nested inside a "parent", field name becomes parent_elem
          field_name = '_'.join((field_name, elem.tag)) if field_name else elem.tag

      else:
        if should_write:

          if should_tag:
            #header_line.append(field_name)  # add field name to csv header
            # remove current tag from the tag name chain
            field_name = field_name.rpartition('_' + elem.tag)[0]
          processed_fields[elem.tag] =('' if elem.text is None else elem.text.strip().replace('"', r'""'))
          #items.append('' if elem.text is None else elem.text.strip().replace('"', r'""'))

        # end of traversing the record tag
        elif elem.tag == tag:
          # csv header (element tag names)
          if self.header_line and not tagged:
            l = []
            for each in processed_fields.keys():
              l.append(re.sub(r'\{.*?\}', '', each))
            new_header = self.map_header(l, self.header_map)
            self.output.write(delimiter.join(new_header) + '\n')
          tagged = True

          # send the csv to buffer
          self.output_buffer.append(r'"' + (r'"' + delimiter + r'"').join(processed_fields.values()) + r'"')
          processed_fields = dict(zip(self.header_line, [" "]*len(self.header_line)))
          n += 1

          # halt if the specified limit has been hit
          if n == limit:
            break

          # flush buffer to disk
          if len(self.output_buffer) > buffer_size:
            self._write_buffer()

        elem.clear()  # discard element and recover memory

    self._write_buffer()  # write rest of the buffer to file
    self.output.close()

    return n


  def _write_buffer(self):
    """Write records from buffer to the output file"""

    self.output.write('\n'.join(self.output_buffer) + '\n')
    self.output_buffer = []

  def map_header(self, header, header_map):
    new_header = []
    for each in header:
      if each in header_map:
        new_header.append(header_map[each])
      else:
        new_header.append(each)
    return new_header



input_file = "/Users/PoojaNihalani/Downloads/dynamiteclothing.xml"
output_file = "/Users/PoojaNihalani/Downloads/dynamiteclothing_new1.csv"
script = xml2csv(input_file, output_file)
script.convert()
