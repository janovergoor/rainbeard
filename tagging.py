"""Tag management module."""

from models import *

# Gets the tagset that 'tagger' has placed on 'target'.
#
# 'tagger' and 'target' are each by specified as a face object.
#
# Returns an object mapping tag names to confidence values. If there is
# no match for any reason, an empty tagset is returned. Does not throw.
def get_tagset(tagger, target):

    # Look up the tagset. If no results are found here, then no tags have been placed.
    try:
        tagset = TagSet.objects.get(tagger=tagger, target=target)
    except TagSet.DoesNotExist:
        return {}

    # Get the tags
    tags = Tag.objects.filter(tagset=tagset).values_list('name', 'confidence')
    return dict((k, v) for (k, v) in tags)


# Sets the tagset that 'tagger' places on 'target'.
#
# 'tagger' and 'target' are each by specified as a face object.
#
# Does not return a value.
def set_tagset(tagger, target, tags):

    # We're going to modify the dict, so make a copy to avoid nasty side effects.
    # NB - We intentionally shadow the method argument here, so that nobody uses
    # it by accident. It's a direct copy, so nobody should need to touch the
    # original.
    tags = tags.copy()

    # Get or create the tagset
    tagset, created = TagSet.objects.get_or_create(tagger=tagger, target=target)

    # Remove all tags that aren't in the new set. Note that, thanks to late
    # evalution of django querysets, this only results in one database query.
    todelete = Tag.objects.filter(tagset=tagset)
    for name, confidence in tags.items():
        todelete = todelete.exclude(name=name)
    todelete.delete()

    # All remaining tags in the database for this TagSet match tags in the new set.
    # However, we don't know if the confidence has changed. Grab them in a single
    # query and only save the ones that changed.
    existing = Tag.objects.filter(tagset=tagset)
    for t in existing:
        if t.confidence != tags[t.name]:
            t.confidence = tags[t.name]
            t.save()
        del tags[t.name]

    # All that's left are the new tags. Hopefully there aren't too many. ;-)
    for name, confidence in tags.items():
        Tag.objects.create(name=name, confidence=confidence, tagset=tagset)
