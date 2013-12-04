# coding: utf-8

from mocker import Mocker
import mocker
import unittest
import ConfigParser
import json

from mocker import ANY, MockerTestCase
from xylose.scielodocument import Article

from citedby import utils
from citedby import controller
import fixtures


class ControllerTests(mocker.MockerTestCase):

    def test_load_document_meta(self):

        article = Article(fixtures.article)

        expected = {'code': u'S0101-31222002000100038',
                    'title': u'Estratégias de luta das enfermeiras da Maternidade Leila Diniz para implantação de um modelo humanizado de assistência ao parto',
                    'issn': u'0101-3122',
                    'source': u'Revista Brasileira de Sementes',
                    'url': u'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0101-31222002000100038'}

        article_meta = controller.load_document_meta(article)

        self.assertEqual(article_meta, expected)

    def test_remove_accents(self):

        self.assertEqual(controller.remove_accents(u'á, b c de F'), u'abcdef')

    def test_load_article(self):
        mock_coll = self.mocker.mock()
        mock_coll.find_one(ANY, ANY)
        self.mocker.result(fixtures.article)
        self.mocker.replay()

        article = controller.load_article(mock_coll, u'S0101-31222002000100038')

        self.assertEqual(article.original_title(), u'Estratégias de luta das enfermeiras da Maternidade Leila Diniz para implantação de um modelo humanizado de assistência ao parto')

    def test_load_article_invalid_article_id(self):
        mock_coll = self.mocker.mock()
        mock_coll.find_one(ANY, ANY)
        self.mocker.result(None)
        self.mocker.replay()

        article = controller.load_article(mock_coll, u'S0101-31222002000100038')

        self.assertEqual(article, None)

    def test_load_article_title_keys(self):

        article = Article(fixtures.article)

        expected = [u'estrategiasdelutadasenfermeirasdamaternidadeleiladinizparaimplantacaodeummodelohumanizadodeassistenciaaoparto',
                    u'nursingfightingstrategiesintheleiladinizmaternitytowardstheimplantationofahumanizedmodelfordeliverycare',
                    u'estrategiasdeluchadelasenfermerasdelamaternidadleiladinizparalaimplantaciondeunmodelohumanizadodeasistenciaalparto']

        self.assertEqual(controller.load_article_title_keys(article), expected)

    def test_query_by_pid(self):
        article = Article(fixtures.article)

        mock_load_article_title_keys = self.mocker.replace(controller.load_article)
        mock_load_article_title_keys(ANY, ANY)
        self.mocker.result(article)

        mock_coll = self.mocker.mock()
        mock_coll.find(ANY, ANY)
        self.mocker.result(fixtures.articles)
        self.mocker.replay()

        expected = { 
                'article':{
                        'code': u'S0101-31222002000100038',
                        'title': u'Estratégias de luta das enfermeiras da Maternidade Leila Diniz para implantação de um modelo humanizado de assistência ao parto',
                        'issn': u'0101-3122',
                        'source': u'Revista Brasileira de Sementes',
                        'url': u'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0101-31222002000100038'
                },
                'cited_by':[{
                        'code': u'S0104-07072013000100023',
                        'title': u'title en',
                        'issn': u'0104-0707',
                        'source': u'Texto & Contexto - Enfermagem',
                        'url': u'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-07072013000100023'
                    },{
                        'code': u'S1414-81452012000300003',
                        'title': u'title pt',
                        'issn': u'1414-8145',
                        'source': u'Escola Anna Nery',
                        'url': u'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S1414-81452012000300003'
                    }
                ]
            }
        self.assertEqual(controller.query_by_pid(mock_coll, 'S0101-31222002000100038'), expected)

    def test_query_by_pid_invalid_article_pid(self):
        mock_load_article_title_keys = self.mocker.replace(controller.load_article)
        mock_load_article_title_keys(ANY, ANY)
        self.mocker.result(None)

        mock_coll = self.mocker.mock()
        self.mocker.replay()

        self.assertEqual(controller.query_by_pid(mock_coll, 'S0101-31222002000100038'), None)

    def test_query_by_pid_without_cited_by(self):
        article = Article(fixtures.article)

        mock_load_article_title_keys = self.mocker.replace(controller.load_article)
        mock_load_article_title_keys(ANY, ANY)
        self.mocker.result(article)

        mock_coll = self.mocker.mock()
        mock_coll.find(ANY, ANY)
        self.mocker.result(None)
        self.mocker.replay()

        expected = { 
                'article':{
                        'code': u'S0101-31222002000100038',
                        'title': u'Estratégias de luta das enfermeiras da Maternidade Leila Diniz para implantação de um modelo humanizado de assistência ao parto',
                        'issn': u'0101-3122',
                        'source': u'Revista Brasileira de Sementes',
                        'url': u'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0101-31222002000100038'
                },
                'cited_by': None
            }

        self.assertEqual(controller.query_by_pid(mock_coll, 'S0101-31222002000100038'), expected)
class SingletonMixinTests(mocker.MockerTestCase):

    def test_without_args(self):
        class Foo(utils.SingletonMixin):
            pass

        self.assertIs(Foo(), Foo())

    def test_single_int_arg(self):
        class Foo(utils.SingletonMixin):
            def __init__(self, x):
                self.x = x

        self.assertIs(Foo(2), Foo(2))

    def test_single_int_kwarg(self):
        class Foo(utils.SingletonMixin):
            def __init__(self, x=None):
                self.x = x

        self.assertIs(Foo(x=2), Foo(x=2))

    def test_multiple_int_arg(self):
        class Foo(utils.SingletonMixin):
            def __init__(self, x, y):
                self.x = x
                self.y = y

        self.assertIs(Foo(2, 6), Foo(2, 6))

    def test_multiple_int_kwarg(self):
        class Foo(utils.SingletonMixin):
            def __init__(self, x=None, y=None):
                self.x = x
                self.y = y

        self.assertIs(Foo(x=2, y=6), Foo(x=2, y=6))

    def test_ConfigParser_arg(self):
        class Foo(utils.SingletonMixin):
            def __init__(self, x):
                self.x = x

        settings = ConfigParser.ConfigParser()
        self.assertIs(
            Foo(settings),
            Foo(settings)
        )


class ConfigurationTests(mocker.MockerTestCase):

    def _make_fp(self):
        mock_fp = self.mocker.mock()

        mock_fp.name
        self.mocker.result('settings.ini')

        mock_fp.readline()
        self.mocker.result('[app]')

        mock_fp.readline()
        self.mocker.result('status = True')

        mock_fp.readline()
        self.mocker.result('')

        self.mocker.replay()

        return mock_fp

    def test_fp(self):
        mock_fp = self._make_fp()
        conf = utils.Configuration(mock_fp)
        self.assertEqual(conf.get('app', 'status'), 'True')

    def test_non_existing_option_raises_ConfigParser_NoOptionError(self):
        mock_fp = self._make_fp()
        conf = utils.Configuration(mock_fp)
        self.assertRaises(
            ConfigParser.NoOptionError,
            lambda: conf.get('app', 'missing'))

    def test_non_existing_section_raises_ConfigParser_NoSectionError(self):
        mock_fp = self._make_fp()
        conf = utils.Configuration(mock_fp)
        self.assertRaises(
            ConfigParser.NoSectionError,
            lambda: conf.get('missing', 'status'))

