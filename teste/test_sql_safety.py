import unittest
from app.main import safe_select

class SQLSafetyTests(unittest.TestCase):
    def test_accepts_basic_select(self):
        self.assertIn("FROM companies", safe_select("SELECT company_name FROM companies"))

    def test_adds_limit_when_missing(self):
        self.assertIn("LIMIT 100", safe_select("SELECT company_name FROM companies"))

    def test_keeps_safe_limit(self):
        self.assertIn("LIMIT 10", safe_select("SELECT company_name FROM companies LIMIT 10"))

    def test_clamps_large_limit(self):
        self.assertIn("LIMIT 100", safe_select("SELECT company_name FROM companies LIMIT 9999"))

    def test_accepts_aggregate(self):
        self.assertIn("COUNT", safe_select("SELECT COUNT(*) FROM companies"))

    def test_accepts_group_by(self):
        self.assertIn("GROUP BY", safe_select("SELECT partner, COUNT(*) FROM companies GROUP BY partner"))

    def test_accepts_order_by(self):
        self.assertIn("ORDER BY", safe_select("SELECT company_name FROM companies ORDER BY expected_value DESC"))

    def test_accepts_markdown_sql_fence(self):
        self.assertIn("SELECT", safe_select("```sql\\nSELECT id FROM companies\\n```"))

    def test_rejects_delete(self):
        with self.assertRaises(ValueError):
            safe_select("DELETE FROM companies")

    def test_rejects_update(self):
        with self.assertRaises(ValueError):
            safe_select("UPDATE companies SET stage='Won'")

    def test_rejects_drop(self):
        with self.assertRaises(ValueError):
            safe_select("DROP TABLE companies")

    def test_rejects_other_table(self):
        with self.assertRaises(ValueError):
            safe_select("SELECT email FROM users")

    def test_rejects_join(self):
        with self.assertRaises(ValueError):
            safe_select("SELECT c.company_name FROM companies c JOIN users u ON 1=1")

    def test_rejects_union(self):
        with self.assertRaises(ValueError):
            safe_select("SELECT company_name FROM companies UNION SELECT email FROM users")

    def test_rejects_multiple_statements(self):
        with self.assertRaises(ValueError):
            safe_select("SELECT company_name FROM companies; DELETE FROM companies")

    def test_rejects_unknown_column(self):
        with self.assertRaises(ValueError):
            safe_select("SELECT password_hash FROM companies")

if __name__ == "__main__":
    unittest.main()
