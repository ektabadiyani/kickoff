from kickoff.traceability import Match, Tracer, normalise, trace_extract


def test_normalise_ignores_markdown_case_and_curly_quotes():
    assert normalise("**Go-live** on “January 15”") == 'go-live on "january 15"'


def test_exact_quote_is_verified(document):
    assert Tracer(document).check("up to fifteen (15) approval workflows in total")[0] is Match.VERIFIED


def test_quote_through_markdown_bold_is_verified(document):
    # The contract has "**Implementation fee:** **$48,000**"; the model will quote it without asterisks.
    assert Tracer(document).check("Implementation fee: $48,000, fixed fee")[0] is Match.VERIFIED


def test_light_paraphrase_is_approximate(document):
    match, similarity = Tracer(document).check("Ledgerline will configure SAML single-sign on with the customer's identity provider (Okta)")
    assert match is Match.APPROXIMATE and similarity >= 0.85


def test_invented_quote_is_not_found(document):
    assert Tracer(document).check("Ledgerline will provide 24/7 phone support for all users")[0] is Match.NOT_FOUND


def test_trace_extract_covers_every_kind_of_item(extract, document):
    results = trace_extract(extract, document)
    kinds = {r.kind for r in results}
    assert kinds == {"requirement", "customer dependency", "risk", "milestone", "exclusion", "payment term"}
    assert all(r.match is Match.VERIFIED for r in results)
