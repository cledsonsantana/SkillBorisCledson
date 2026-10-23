"""Public package guardrails. No patient data or live integrations."""
import pathlib,re,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
PAYLOAD=ROOT/'skills/scientific-article-appraisal'

def public_files():
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in ('.git','__pycache__','.venv','outputs') for p in path.relative_to(ROOT).parts):
            continue
        yield path

class ReleaseContract(unittest.TestCase):
    def test_agent_entry_and_human_documents_exist(self):
        for name in ('AGENTS.md','INSTALL.md','README.md','LICENSE','THIRD_PARTY.md','SECURITY.md','CONTRIBUTING.md','docs/METODO.md','docs/INSTRUMENTOS.md','scripts/install_skill.py','examples/synthetic/record.json','examples/synthetic/source.txt'):
            self.assertTrue((ROOT/name).is_file(),name)

    def test_skill_identity_and_version_are_coherent(self):
        text=(PAYLOAD/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        front=text.split('---',2)[1]
        self.assertRegex(front,r'(?m)^name: scientific-article-appraisal$')
        description=re.search(r'(?m)^description:\s*(.+)$',front).group(1).strip('"\'')
        self.assertLessEqual(len(description),60)
        self.assertTrue(description.endswith('.'))
        self.assertRegex(front,r'(?m)^\s*version:\s*["\']?0\.6\.0')
        self.assertIn('0.6.0',(ROOT/'README.md').read_text(encoding='utf-8'))
        self.assertRegex(front,r'(?m)^license: MIT$')

    def test_public_tree_has_no_private_artifacts_or_secret_patterns(self):
        secret=re.compile(r'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----')
        private=re.compile(r'/r[o]ot/|/etc/easy[p]anel/|(?:docs|drive)\.google\.com/(?:document|drive|file)/',re.I)
        for path in public_files():
            self.assertNotIn(path.suffix.lower(),('.pdf','.docx','.xlsx','.pem','.key','.p12','.pfx','.pyc'),str(path))
            self.assertFalse(path.name.startswith('.env'),str(path))
            if path.suffix in ('.md','.py','.json','.txt','.yml','.yaml') or path.name=='LICENSE':
                text=path.read_text(encoding='utf-8')
                self.assertIsNone(secret.search(text),str(path))
                # This guard's regex literals are not source-specific private values.
                self.assertIsNone(private.search(text),str(path))

    def test_relative_markdown_links_resolve(self):
        for path in public_files():
            if path.suffix!='.md':continue
            text=path.read_text(encoding='utf-8')
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
                target=target.split('#',1)[0]
                if not target or '://' in target or target.startswith('mailto:'):continue
                self.assertTrue((path.parent/target).is_file(),f'{path.relative_to(ROOT)} -> {target}')

    def test_instrument_categories_and_synthetic_limits_are_documented(self):
        text=(ROOT/'docs/INSTRUMENTOS.md').read_text(encoding='utf-8')
        for instrument in ('AMSTAR 2','ROBIS','RoB 2','ROBINS-I','JBI','COSMIN','QUADAS','PEDro','GRADE','PRISMA','CONSORT','STROBE','SPIRIT','TIDieR'):
            self.assertIn(instrument,text)
        source=(ROOT/'examples/synthetic/source.txt').read_text(encoding='utf-8')
        self.assertIn('NÃO É ARTIGO NEM EVIDÊNCIA CLÍNICA',source)
        self.assertIn('não é um arquivo de configuração',(ROOT/'INSTALL.md').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
