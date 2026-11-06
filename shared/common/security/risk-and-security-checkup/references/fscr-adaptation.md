# Repository conventions used by this adaptation

The uploaded version 2.2.6 package supplies normalization, rule generation, and
evaluation logic. The FSCR adaptation uses the repository manifest schema,
project persistence, token tracking, and routed core-service execution boundaries.

Environment handling follows the local
[core REST client](../../../../../core/fusion-api/rest-api-client/SKILL.md):
`fusion_environment_context` comes from the active workflow, and the selected
properties file supplies `environment` and `restBaseUrl`. Authentication follows
[core OAuth](../../../../../core/auth/fusion-oauth-authentication/SKILL.md);
the checkup does not solicit host prefixes, application usernames, or secrets.

When a workflow actually requires the signed-in identity, it resolves that
identity through the declared Core route. This assessment does not require a
login username.

The skill is shared assessment guidance that can be consumed across pillars. It
does not claim an FSM task code or catalog registration. Its extraction planner
delegates current-run BOSS reads through the Core skill.
Keep FSCR manifest fields at the top level as required by
`schemas/skill-manifest.schema.json`. Skill discovery uses the repository's
`SKILL.md` metadata and its `shared.common.security.risk-and-security-checkup` identity.
