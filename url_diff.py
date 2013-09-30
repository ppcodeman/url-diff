#!/usr/bin/python2
"""A tool to show the differnce in URLs.

A tool for showing the differnces between URLs.  This is inspired by the unix
utility diff.
"""

import argparse
import copy
import logging
import sys

class Error(Exception):
  """Base exception class."""
  pass

class ParamDiffTypeError(Error):
  """Raised when an incorrect diff type used."""
  pass

class HostnameParseError(Error):
  """Raised when unable to parse hostname from URL."""
  pass

# TODO(macpd): investigate making this a namedtuple
class ParamDiffEntry(object):
  """Represents difference of 2 URL params with same name."""
  LEFT_ONLY = 1
  RIGHT_ONLY = 2
  BOTH_DIFFER = 3
  left_value_format = '{0}\n< {1}'
  right_value_format = '{0}\n> {1}'

  def __init__(self, name, left_value, right_value, diff_type, unified):
    self._name = name
    self._left_val = left_value
    self._right_val = right_value
    if unified:
      self.left_value_format = '{0}\n- {1}'
      self.right_value_format = '{0}\n+ {1}'
    try:
      if self._valid_diff_type(diff_type):
        self._type = diff_type
    except ParamDiffTypeError:
      logging.error("Incorrect diff type: %s", diff_type)
      self._type = self.BOTH_DIFFER

  def _valid_diff_type(self, diff_type):
    if (diff_type != self.LEFT_ONLY and diff_type != self.RIGHT_ONLY and
        diff_type != self.BOTH_DIFFER):
      raise ParamDiffTypeError('%s is not a valid diff type. ', diff_type)
    return True

  @property
  def name(self):
    return self._name

  def __str__(self):
    ret = self._name
    if self._type == self.LEFT_ONLY or self._type == self.BOTH_DIFFER:
      ret = self.left_value_format.format(ret, self._left_val)
    if self._type == self.RIGHT_ONLY or self._type == self.BOTH_DIFFER:
      ret = self.right_value_format.format(ret, self._right_val)
    return ret


class UrlDiffer(object):
  """Object to diff URLs.

  Diffs URLs upon intialization."""

  PATH_DELIM = '?'
  PARAM_DELIM = '&'
  NAME_VAL_DELIM = '='
  SCHEME_DELIM = '://'

  def __init__(self, left_url, right_url, names_only=False, hostnames=False, unified=False):
    """Initializes object and performs URL diffing."""
    self._left_url = self._normalize_url(left_url)
    self._right_url = self._normalize_url(right_url)
    self._names_only = names_only
    self._wants_hostname_diff = hostnames
    self._unified = unified
    self._diffs = []
    self._do_diff()

  def __str__(self):
    ret = []
    for diff in self._diffs:
      if self._names_only:
        ret.append(diff.name)
      else:
        ret.append(str(diff))
    join_delim = '\n' if self._names_only else '\n\n'
    return join_delim.join(ret)

  def _normalize_url(self, url):
    """Strips white space, and removes all chars after #"""
    ret = url.strip()
    if '#' in ret:
      idx = ret.index('#')
      ret = ret[:idx]
    return ret

  def _get_hostname(self, url):
    """Parses the hostname from a URL."""
    try:
      scheme_idx = url.find(self.SCHEME_DELIM)
      if scheme_idx == -1:
        hostname_begin = 0
        if not url[hostname_begin].isalnum():
          raise ValueError
      else:
        hostname_begin = scheme_idx + len(self.SCHEME_DELIM)
      hostname_end = url.index('/', hostname_begin)
      return url[hostname_begin:hostname_end]
    except ValueError:
      logging.error('Unable to parse hostname from %s', url)
      raise HostnameParseError

  def _diff_hostnames(self, left, right):
    """Diffs hostnames, if different appends ParamDiffEntry to diffs list.

    Args:
      left: String; left hostname.
      right: String; right hostname.
    Returns:
      Bool; True if different, else False.
    """
    if left == right:
      self._hostnames_differ = False
    else:
      self._hostnames_differ = True
      self._diffs.append(ParamDiffEntry('Hostname', left, right,
          ParamDiffEntry.BOTH_DIFFER, self._unified))

    return self._hostnames_differ

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

  def _diff_params(self, left_params, right_params):
    """Returns a list of the diffence between dicts on key/values.

    Args:
      left_param: dict; param name -> value dict of the left URL.
      right_param: dict; param name -> value dict of the right URL.

    Returns:
      dict of ParamDiffEntry of differences between the left and right params.
    """
    diffs = []
    for left_key in left_params.iterkeys():
      if left_key in right_params:
        if left_params[left_key] != right_params[left_key]:
          diffs.append(ParamDiffEntry(
            left_key, left_params[left_key], right_params[left_key],
            ParamDiffEntry.BOTH_DIFFER, self._unified))
      else:
        diffs.append(ParamDiffEntry(
          left_key, left_params[left_key], None, ParamDiffEntry.LEFT_ONLY, self._unified))

    for right_key in right_params.iterkeys():
      if right_key not in left_params:
        diffs.append(ParamDiffEntry(
          right_key, None, right_params[right_key], ParamDiffEntry.RIGHT_ONLY, self._unified))

    return diffs

  def _do_diff(self):
    """Performs all appropriate diffing operations."""
    if self._wants_hostname_diff:
      self._left_hostname = self._get_hostname(self._left_url)
      self._right_hostname = self._get_hostname(self._right_url)
      self._diff_hostnames(self._left_hostname, self._right_hostname)
    self._left_params_dict = self._get_params(self._left_url)
    self._right_params_dict = self._get_params(self._right_url)
    self._diffs.extend(self._diff_params(
      self._left_params_dict, self._right_params_dict))

  def left_params(self):
    """Returns a deep coy of the left params dict."""
    return copy.deepcopy(self._left_params_dict)

  def right_params(self):
    """Returns a deep coy of the left params dict."""
    return copy.deepcopy(self._right_params_dict)

  def are_different(self):
    """Returns True if URLs differ, else false."""
    return len(self._diffs) != 0

  @property
  def diff(self):
    return copy.deepcopy(self._diffs)


def main():
  # TODO(macpd): main function documentation
  # TODO(macpd): usage string
  # TODO(macpd): provide option to url decode params before comparison
  # TODO(macpd): provide option to diff case insensitively
  arg_parser = argparse.ArgumentParser(
      description='show the difference between 2 urls. Inspired by the unix utility diff',
      epilog='Currenty this tool discards everything after # if present.')
  arg_parser.add_argument('--hostname', default=False, required=False,
      help='also diff URL hostname', action='store_true', dest='diff_hostname')
  arg_parser.add_argument('--names', '-n', default=False, required=False,
      help='only diff URL parameter names.', action='store_true', dest='names_only')
  arg_parser.add_argument('--unified', '-u', default=False, required=False,
      help='use unified mode + / - instead of < >', action='store_true', dest='unified')
  arg_parser.add_argument('left_url', type=str, help='URL to diff against.  logically handled as the left argurmnt of diff.', metavar='<left URL>')
  arg_parser.add_argument('right_url', type=str, help='URL to diff against.  logically handled as the left argurmnt of diff.', metavar='<right URL>')

  args = arg_parser.parse_args()

  differ = UrlDiffer(args.left_url, args.right_url, names_only=args.names_only,
      hostnames=args.diff_hostname, unified=args.unified)

  print differ

  sys.exit(1 if differ.are_different() else 0)

if __name__ == '__main__':
  main()
