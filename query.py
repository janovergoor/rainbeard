from rainbeard.models import *

#
# Code for performing rainbeard queries.
#

#
# Generates a tag cloud about 'target' from the perspective of 'source'.
#
# The returned tag cloud is a dictionary mapping tag names to strength values.
#
def do_query(source, target):
  
  # Retrieve tag set from the source to the target
  # Note : assumes that there exists one
  tagSet = TagSet.objects.filter(tagger=Face.objects.get(pk = source.pk),
                                 target=Face.objects.get(pk = target.pk))

  # Retrieve the tags in the tag set
  tags = Tag.objects.filter(tagset=tagSet.get())
  
  # Turn results into a dictionary
  results = dict([(tag.name, tag.confidence) for tag in tags])
  
  return results
