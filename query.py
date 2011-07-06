"""Confidant network query module."""

import models


def do_query(source, target):
    """
    Generates a tag cloud about 'target' from the perspective of 'source'.

    The returned tag cloud is a dictionary mapping tag names to strength
    values.

    NOTE: This code is only to test the importing of fixtures, it will be
    replaced by actual query code.
    """

    # Retrieve tag set from the source to the target.
    tagSet = TagSet.objects.filter(tagger=Face.objects.get(pk=source.pk),
                                   target=Face.objects.get(pk=target.pk))

    # Retrieve the tags in the tag set
    tags = Tag.objects.filter(tagset=tagSet.get())

    # Turn results into a dictionary
    results = dict([(tag.name, tag.confidence) for tag in tags])

    return results
