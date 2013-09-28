#!/usr/bin/python2
"""One-line documentation for url_params module.

A detailed description of url_params.
"""

import argparse
import sys

# def get_params(url):
#   """Returns a dict of the url params."""
#   param_dict = {}
#   if '?' not in url:
#     return param_dict
#   params_pos = url.find('?') + 1
#   for token in url[params_pos:].split('&'):
#     if '=' not in token:
#       continue
#     partitioned_param = token.partition('=')
#     param_dict[partitioned_param[0]] = partitioned_param[2]
#   return param_dict

# def diff_params(left_params, right_params, names_only=False):
#     for left_key in left_params.iterkeys():
#       if left_key in right_params:
#         if left_params[left_key] != right_params[left_key]:
#           print left_key
#           if not names_only;
#             print '< %s' % (left_params[left_key])
#             print '> %s\n' % (right_params[left_key])
#       else:
#         print left_key
#         if not names_only:
#           print '< %s\n' % (left_params[left_key])

#   for right_key in right_params.iterkeys():
#     if right_key not in left_params:
#       print right_key
#       if right_params[right_key] != left_params[right_key]:
#         print '< %s' % (left_params[right_key])
#         print '> %s\n' % (right_params[right_key])
#       print

class Url_Differ():

  PATH_DELIM = '?'
  PARAM_DELIM = '&'
  NAME_VAL_DELIM = '='

  def __init__(self, left_url, right_url, names_only=False):
    self._left_url = left_url
    self._right_url = right_url
    self._names_only = names_only


  def _get_params(self, url):
    """Returns a dict of the url params."""
    param_dict = {}
    if self.PATH_DELIM not in url:
      return param_dict
    params_pos = url.find(self.PATH_DELIM) + 1
    for token in url[params_pos:].split(self.PARAM_DELIM):
      if '=' not in token:
        continue
      partitioned_param = token.partition(self.NAME_VAL_DELIM)
      param_dict[partitioned_param[0]] = partitioned_param[2]
    return param_dict

  def _diff_params(self, left_params, right_params, names_only=False):
    """Returns a list of the diffence between dicts on key/values.

    """
    # TODO(macpd) put output in string instead of printing
    diffs = []
    for left_key in left_params.iterkeys():
      if left_key in right_params:
        if left_params[left_key] != right_params[left_key]:
          diffs.append(left_key)
          if not names_only:
            diffs.append('< %s' % (left_params[left_key]))
            diffs.append('> %s' % (right_params[left_key]))
      else:
        diffs.append(left_key)
        if not names_only:
          diffs.append('< %s' % (left_params[left_key]))

    for right_key in right_params.iterkeys():
      if right_key not in left_params:
        diffs.append(right_key)
        if not names_only:
          diffs.append('> %s' % (right_params[right_key]))

    return diffs

  def __str__(self):
    left_params_dict = self._get_params(self._left_url)
    right_params_dict = self._get_params(self._right_url)
    diffs = self._diff_params(left_params_dict, right_params_dict, self._names_only)
    return '\n'.join(diffs)


  def print_diff(self):
    print self


def print_usage(self):
  """Prints intended usage."""
  print "%s: <flags> url url" % (self.__class__.__name__)


def main():
  # TODO(macpd): main function documentation
  # TODO(macpd): usage string
  arg_parser = argparse.ArgumentParser()
  # TODO(macpd): match domain and hostname
  arg_parser.add_argument('--hostname', default=False, required=False,
      help='also diff URL hostname', action='store_true', dest='diff_hostname')
  # TODO(macpd): match URL param names
  arg_parser.add_argument('-n', '--names', default=False, required=False,
      help='only diff URL parameter names.', action='store_true', dest='names_only')
  arg_parser.add_argument('left_url', type=str, help='URL to diff against.  logically hadled as the left argurmnt of diff.', metavar='<left URL>')
  arg_parser.add_argument('right_url', type=str, help='URL to diff against.  logically hadled as the left argurmnt of diff.', metavar='<right URL>')

  args = arg_parser.parse_args()


  # if len(sys.argv) != 2:
  #   print_usage()
  #   sys.exit(-1)

  differ = Url_Differ(args.left_url, args.right_url, args.names_only)
  print differ
  # differ.print_diff()


if __name__ == '__main__':
  main()
