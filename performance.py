# Copyright (c) 2009 Stefan Marr <http://www.stefan-marr.de/>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import re

class Performance:
  """Performance provides a common interface and some helper functionality
     to evaluate the output of benchmarks and to determine measured performance
     values.
  """
  
  # definition of some regular expression to identify erroneous runs
  re_error    = re.compile("Error")
  re_segfault = re.compile("Segmentation fault")
  re_buserror = re.compile("Bus error") 
  
  def acquire_command(self, command):
    return command

  def parse_data(self, data):
    pass

  def check_for_error(self, line):
    """Check whether the output line contains one of the common error
       messages. If its an erroneous run, the result has to be discarded.
    """
    if self.re_error.search(line):
      return True
    if self.re_segfault.search(line):
      return True
    if self.re_buserror.search(line):
      return True
    
    return False

class LogPerformance(Performance):
  """LogPerformance is the standard for ReBench.
     It is used to read a simple log format which includes the number of iterations of
     a benchmark and its runtime in microseconds.
  """
  re_logline  = re.compile(r"^(?:.*: )?(\w+)( \w+)?: iterations=([0-9]+) runtime: ([0-9]+)([mu])s")

  def parse_data(self, data):
    result = []
    total = None
     
    for line in data.split("\n"):
      if self.check_for_error(line):
        return None
    
      m = self.re_logline.match(line)
      if m:
        time = float(m.group(4))
        if m.group(5) == "m":
          time = time * 1000
        criterion = (m.group(2) or 'total').strip()
        
        result.append({ 'bench': m.group(1), 'subCriterion':criterion, 'time':time })
        
        if criterion == 'total':
            assert total == None, "benchmark run returned more than one 'total' value"
            total = time
        
    return (total, result)

class TimePerformance(Performance):
  """TimePerformance uses the systems time utility to allow measurement of
     unmodified programs or aspects which need to cover the whole program
     execution time.
  """
  re_time  = re.compile(r"^(\w+)\s*(\d+)m(\d+\.\d+)s")

  def acquire_command(self, command):
    return "/usr/bin/time -p %s"%(command)

  def parse_data(self, data):
    result = []
    total = None
      
    for line in data.split("\n"):
      if self.check_for_error(line):
        return None
        
      m = re_time.match(line)
      if m:
        criterion = 'total' if m.group(1) == 'real' else m.group(1)
        time = (float(m.group(2)) * 60 + float(m.group(3))) * 1000 * 1000
        result.append({ 'bench': None, 'subCriterion':criterion, 'time':time })
        
        if criterion == 'total':
            assert total == None, "benchmark run returned more than one 'total' value"
            total = time
    
    return (total, result)

class TestPerformance(Performance):
    
    test_data = [45872, 45871, 45868, 45869, 45873,
                 45865, 45869, 45874, 45863, 45873,
                 45872, 45873, 45867, 45872, 45876,
                 45871, 45870, 45870, 45868, 45869,
                 45872, 45873, 45867, 45866, 45869,
                 45875, 45871, 45869, 45870, 45874]
    index = 0
    
    def parse_data(self, data):
        result = self.test_data[self.index]
        self.index = (self.index + 1) % len(self.test_data)
        return result

