# AGENTS Notes

## Repo-specific context

- `core_lib/helpers/shell_utils.py` currently exposes `prompt_*` helpers, not `input_*` helpers and not `prompt__*` helpers.
- The active public prompt helpers are:
  - `prompt_string`
  - `prompt_str`
  - `prompt_file_name`
  - `prompt_yes_no`
  - `prompt_bool`
  - `prompt_int`
  - `prompt_email`
  - `prompt_url`
  - `prompt_timeframe`
  - `prompt_enum`
  - `prompt_options`
  - `prompt_list`
  - `prompt_comma_list`

## Recent migration we completed

- Generator modules previously imported old `input_*` names from `core_lib.helpers.shell_utils`.
- Those imports and usages were updated to the new `prompt_*` names across:
  - `core_lib_generator/config_collectors/`
  - `core_lib_generator/core_lib_config_generate_yaml.py`
  - `core_lib_generator/generator_utils/helpers.py`
- A repo-wide scan confirmed there are no remaining `input_*` imports or `shell_utils` prompt call sites left to migrate.
- The only remaining text like `input_list` is a local variable name in tests, not an import from `shell_utils`.

## SonarCloud follow-up

- SonarCloud reported:
  - `prompt_str` had cognitive complexity 17 and needed to be reduced to 15 or less.
  - Nested conditional-expression warnings existed around `prompt_url`, `prompt_timeframe`, `prompt_enum`, and `prompt_list`.
- We addressed this by introducing small private helpers in `core_lib/helpers/shell_utils.py`:
  - `_empty_prompt_result`
  - `_coalesce_prompt_value`
- These helpers keep behavior the same while reducing branching and removing nested conditional expressions.

## Exact SonarCloud items from PR 164

- File: `core_lib/helpers/shell_utils.py`
- Function: `prompt_str`
  - Sonar comment: `Refactor this function to reduce its Cognitive Complexity from 17 to the 15 allowed.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2T&open=AZ15FO8tgeiY87x_QG2T&pullRequest=164`
- Function: `prompt_url`
  - Original reported line: `148`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2U&open=AZ15FO8tgeiY87x_QG2U&pullRequest=164`
- Function: `prompt_timeframe`
  - Original reported line: `159`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2V&open=AZ15FO8tgeiY87x_QG2V&pullRequest=164`
- Function: `prompt_enum`
  - Original reported line: `178`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2W&open=AZ15FO8tgeiY87x_QG2W&pullRequest=164`
- File location around original line: `207`
  - Sonar link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2X&open=AZ15FO8tgeiY87x_QG2X&pullRequest=164`
  - Note: the pasted report did not include the textual message for this one, only the issue link and `/ SonarCloud Code Analysis`.
- Function: `prompt_list`
  - Original reported line: `221`
  - Sonar comment: `Extract this nested conditional expression into an independent statement.`
  - Link: `https://sonarcloud.io/project/issues?id=shay-te_core-lib&issues=AZ15FO8tgeiY87x_QG2Y&open=AZ15FO8tgeiY87x_QG2Y&pullRequest=164`

## Mapping of the fix to those Sonar items

- `prompt_str` was simplified by delegating empty/default/none handling to `_empty_prompt_result`.
- The nested conditional expressions reported for `prompt_url`, `prompt_timeframe`, `prompt_enum`, and `prompt_list` were replaced with `_coalesce_prompt_value(...)`.
- Current line numbers in `shell_utils.py` have shifted after the refactor, so the Sonar-reported line numbers above refer to the older pre-fix version from PR 164.

## Verification we ran

- `python -m pytest tests/test_command_line.py`
- Import smoke test for the updated generator modules:
  - `python -c "import core_lib_generator.config_collectors.setup_collector, core_lib_generator.config_collectors.data_access, core_lib_generator.config_collectors.cache, core_lib_generator.config_collectors.database, core_lib_generator.config_collectors.job, core_lib_generator.config_collectors.solr, core_lib_generator.config_collectors.db_entity, core_lib_generator.config_collectors.service, core_lib_generator.core_lib_config_generate_yaml, core_lib_generator.generator_utils.helpers"`

## Practical guidance for future edits

- If prompt-related code changes again, treat `core_lib/helpers/shell_utils.py` as the source of truth for exported names.
- Before mass-renaming prompt helpers, scan the repo with `rg` for both imports and call sites.
- Keep prompt helpers simple because this repo is checked by SonarCloud and small readability warnings can block PRs.
