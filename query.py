import time
from models import *

verbose = False # print analytics or not

#
# Code for performing rainbeard queries.
#
  
#
# Generates a tag cloud about 'target' from the perspective of 'source'.
# The returned tag cloud is a dictionary mapping tag names to strength values.
#
def do_query(network, source, target):
  
  # retrieve all existing tag sets for the target
  tagSets = TagSet.objects.filter(target=Face.objects.get(pk= target.pk))  
  
  # extract the allowed targets for the graph search algorithm
  targets = [x.tagger.pk for x in tagSets]
    
  # find n best paths between source and targets
  paths = find_paths(network, source.pk, targets)
    
  # collect the resulting tag sets
  result_set = {}
  for x in paths:
    
    # look up the tags associated by x[0][-1] 
    temp_tags = Tag.objects.filter(tagset=tagSets.get(tagger=x[0][-1]))
    
    # add each tag to the result set
    for tag in temp_tags:
      score = tag.confidence * x[1]  # weight by path cost
      if tag.name in result_set:
        result_set[tag.name] += score
      else:
        result_set[tag.name] = score

  return result_set


#
# Finds n paths between the source node and one of the possible target nodes
# Uses a best-first graph search algorithm based on A* with a heuristic of h(x)=0
#
def find_paths(network, source, targets):

  n = 1  # number of paths to be found

  found_paths = [] # the paths already found between source and target
  fronts      = { (source,) : 1 } # the paths currently under consideration

  startTime   = time.time() 
  c1          = 0 # the number of heads considered
  c2          = 0 # the number of paths expanded

  while True:

    # take best path and remove it from fronts
    # NB: this is very inefficient : it sorts the heads at each iteration...
    head = sorted(fronts.iteritems(), key=lambda (k,v): v, reverse=True)[0] # head = (path,cost)
    del fronts[head[0]] 
    c1 += 1

    # if current best path reaches the target, add it to found_paths
    if head[0][-1] in targets:
      found_paths.append(head)
      if verbose:
        print "Path found: ", head[0], "  with cost: ", head[1]

    # break condition
    if len(found_paths) == n:
      break

    # expand the head, add next nodes to the stack
    links = network.get_confidants(head[0][-1]) # find all links coming from the head
    if links != 0:  # check if there are sucessor nodes
      for x in links: # iterate over sucessor nodes
        if x[1] not in head[0]: # remove paths going through nodes already seen
          new_path = head[0] + (x[1],) # create new path
          fronts[new_path] = head[1]*x[0]
          c2 += 1

  if verbose:
    print '\nAnalytics'
    print 'Nodes in the network:', len(nodes)
    print "#c1 steps:", c1
    print "#c2 steps:", c2
    print "Took", time.time()-startTime, "seconds to run"

  return found_paths