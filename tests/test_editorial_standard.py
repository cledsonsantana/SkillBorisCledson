"""Behavioral documentation contract for the public clinical editorial standard."""
import pathlib,re,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
PAYLOAD=ROOT/'skills/scientific-article-appraisal'

class EditorialStandard(unittest.TestCase):
    def test_new_method_references_are_available_and_required(self):
        skill=(PAYLOAD/'SKILL.md').read_text(encoding='utf-8')
        for name in ('methodological-panel.md','rct-source-and-result-audit.md'):
            self.assertTrue((PAYLOAD/'references'/name).is_file(),name)
            self.assertIn('references/'+name,skill)

    def test_clinical_pass_is_integral_and_separate_from_data_checks(self):
        guide=(PAYLOAD/'references/clinician-readable-interpretation.md').read_text(encoding='utf-8')
        for term in ('Revisão de linguagem antes da entrega','Padrão clínico obrigatório de entrega','justificativas','auditoria semântica','hash','keepWithNext'):
            self.assertIn(term,guide)
        self.assertIn('revisão editorial integral',(PAYLOAD/'SKILL.md').read_text(encoding='utf-8'))

    def test_panels_keep_native_units_without_a_universal_score(self):
        path=PAYLOAD/'references/methodological-panel.md'
        self.assertTrue(path.is_file(),'Native categorical panels are not documented')
        guide=path.read_text(encoding='utf-8')
        for term in ('AMSTAR 2','ROBIS','RoB 2','faixa única','quadrado','fundo branco','0–100','SEM CLASSIFICAÇÃO GLOBAL NATIVA'):
            self.assertIn(term,guide)
        self.assertIn('painel metodológico',(PAYLOAD/'templates/article-review.md').read_text(encoding='utf-8').lower())

    def test_rct_audit_distinguishes_measurement_imputation_and_reanalysis(self):
        path=PAYLOAD/'references/rct-source-and-result-audit.md'
        self.assertTrue(path.is_file(),'Result-level RCT source audit is missing')
        guide=path.read_text(encoding='utf-8')
        for term in ('imputação','observação','pontos percentuais','ANOVA','autorrelato','RoB 2','algoritmos nativos'):
            self.assertIn(term,guide)

    def test_context_is_user_supplied_not_an_implicit_organization(self):
        skill=(PAYLOAD/'SKILL.md').read_text(encoding='utf-8')
        template=(PAYLOAD/'templates/article-review.md').read_text(encoding='utf-8')
        self.assertIn('Não presuma instituição',skill)
        self.assertIn('contexto-alvo informado',template)
        for name in ('SKILL.md','templates/article-review.md','references/clinician-readable-interpretation.md','references/methodological-panel.md','references/rct-source-and-result-audit.md'):
            path=PAYLOAD/name
            if path.exists():
                text=path.read_text(encoding='utf-8')
                self.assertNotRegex(text,r'\bRede\s+[A-Z][A-Z]+\b',name)
                self.assertNotRegex(text,r'/(?:root|home/[^/\s]+)/',name)

if __name__=='__main__':unittest.main()
