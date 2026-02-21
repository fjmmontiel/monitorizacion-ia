import textwrap

import pytest

from orchestrator.core.use_case_loader import UseCaseLoader


def test_http_proxy_requires_dashboard_detail_id_template(tmp_path):
    cfg = textwrap.dedent(
        """
        use_cases:
          hipotecas:
            adapter: http_proxy
            upstream:
              base_url: http://localhost:9000
              routes:
                cards: /cards
                dashboard: /dashboard
                dashboard_detail: /dashboard_detail
        """
    )
    config_path = tmp_path / 'invalid.yaml'
    config_path.write_text(cfg, encoding='utf-8')

    with pytest.raises(Exception):
        UseCaseLoader(str(config_path)).load()
