# -*- coding: utf-8 -*-
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('geo_ko')

def kotti_configure(settings):

    settings['pyramid.includes'] += ' geo_ko geo_ko.views'


def includeme(config):
    pass
    #config.add_translation_dirs('geo_ko:locale')

