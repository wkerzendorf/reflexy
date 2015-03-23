import unittest
from reflexy.base import reflex


class TestReflexModule(unittest.TestCase):
    sof = 'datasetname|file1.fits;PRO_CATG1;PURPOSE1:PURPOSE2,file2;' \
          'PRO_CAT2;PURPOSE1'
    sopexp = [('long_param1', '3'), ('param2', '3'), ('param3', 'ser'),
              ('param_not_shown', 'none')]
    sop = 'recipe_name:long_param1=3,recipe_name:param2=3,' \
          'recipe_name:param3=ser,recipe_name:param_not_shown=none'

    def test_parseSof(self):
        r = reflex.parseSof(self.sof)
        self.assertEqual(len(r), 2)
        self.assertEqual(r.datasetName, 'datasetname')
        f1, f2 = r.files
        self.assertEqual(f1.name, 'file1.fits')
        self.assertEqual(f1.category, 'PRO_CATG1')
        self.assertEqual(len(f1.purposes), 2)
        self.assertIn('PURPOSE1', f1.purposes)
        self.assertIn('PURPOSE2', f1.purposes)

        self.assertEqual(f2.name, 'file2')
        self.assertEqual(f2.category, 'PRO_CAT2')
        self.assertEqual(len(f2.purposes), 1)
        self.assertEqual(f2.purposes[0], 'PURPOSE1')

    def test_parseRoundTripJson(self):
        r = reflex.parseSof(self.sof)
        j = r.toJSON()
        r2 = reflex.parseSofJson(j)
        self.assertEqual(r, r2)

    def test_parseSop(self):
        r = reflex.parseSop(self.sop)
        self.assertEqual(len(r), len(self.sopexp))
        for p, ep in zip(r, self.sopexp):
            self.assertEqual(p.recipe, 'recipe_name')
            self.assertEqual(p.displayName, ep[0])
            self.assertEqual(p.value, ep[1])

if __name__ == "__main__":
    unittest.main()
