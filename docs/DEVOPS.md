# DevOps guide

How a change travels from a branch to a published, checked container image, and how to observe and roll back the service.

## Pipeline

```
branch -> commit -> push -> pull request -> CI -> merge to main -> release -> staging check
                                             |
                                             +-- test        pytest (20 tests)
                                             +-- docker      build image, start container, smoke-test /predict
                                             +-- monitoring  app + Prometheus + Grafana, verify metrics and dashboard
```

| Stage | Trigger | What runs | Where to see it |
|---|---|---|---|
| Test | every push and pull request | `pytest` on a clean Ubuntu runner | Actions tab |
| Docker | after Test | build image, run container, request a real prediction | Actions tab |
| Monitoring | after Test | `docker compose` brings up app, Prometheus and Grafana; CI checks the scrape and the dashboard | Actions tab |
| Release | push to `main` or a `v*` tag, after all checks pass | build and publish `ghcr.io/<owner>/fraud-detection` tagged `sha-<commit>` and `latest` (plus the version on tags) | repo "Packages" |
| Staging | after Release | pull the exact published image and verify it serves predictions and metrics | Actions tab, `staging` environment |
| GitHub Release | push of a `v*` tag, after Staging | create a release with generated notes | repo "Releases" |

Pushes to `main` and version tags are the only ones that publish an image. Feature branches run the checks only.

## Making a change (pull-request workflow)

```bash
git switch -c fix/short-description
# edit, test locally
python -m pytest tests
git add -A && git commit -m "Describe the change"
git push -u origin fix/short-description
```

Open a pull request on GitHub, wait for the CI checks to go green, ask a teammate to review, then merge. Never push straight to `main`.

## Monitoring

```bash
docker compose -f deploy/monitoring/docker-compose.yml up --build
```

| Service | URL | Notes |
|---|---|---|
| App | http://localhost:8000 | dashboard, API, `/metrics` |
| Prometheus | http://localhost:9090 | scrapes `/metrics` every 5 s |
| Grafana | http://localhost:3000 | login `admin` / `admin`; dashboard **Fraud API** is pre-loaded |

Metrics exposed by the API:

| Metric | Meaning |
|---|---|
| `fraud_api_requests_total{method,path,status}` | requests handled |
| `fraud_api_request_seconds` | latency histogram per endpoint |
| `fraud_predictions_total{prediction,risk_level}` | predictions served, by verdict |
| `fraud_model_loaded` | 1 when the model is loaded, 0 otherwise |
| `fraud_prediction_probability` | histogram of predicted fraud scores (use it to watch score drift) |

### Two ways to watch the model

| | Built-in Monitoring pane | Prometheus and Grafana |
|---|---|---|
| Where | the **Monitoring** section of the dashboard (`/monitoring/summary`) | `docker compose -f deploy/monitoring/docker-compose.yml up` |
| Extra services | none | Prometheus and Grafana |
| History | last 30 minutes, resets on restart | as long as Prometheus keeps it |
| Good for | day-to-day: is it up, what is it predicting, is the score distribution drifting | long-term trends, several services, alerts |

The pane shows request, prediction and error rates, the flag rate against the test-set baseline, p50 and p95 latency, verdict and risk mix, the live score distribution against the test set, and the latest predictions. Use *Send 20 sample predictions* to see it move.

Try it: open the Grafana dashboard, use the app's dashboard to analyse a few transactions, and watch the panels move.

## Rollback

Every release is an immutable image tagged with its commit. To go back to a known-good version:

```bash
# list tags on GitHub: repo -> Packages -> fraud-detection
docker pull ghcr.io/s-tarakramreddy/fraud-detection:sha-<known-good-commit>
docker run -d -p 8000:8000 ghcr.io/s-tarakramreddy/fraud-detection:sha-<known-good-commit>
```

In git terms, undo a bad change with `git revert <commit>` on a branch and merge it through a pull request, so the pipeline checks the fix as well.

## Cutting a versioned release

```bash
git tag v1.0.0
git push origin v1.0.0
```

The pipeline runs all checks, publishes the image as `1.0.0`, runs the staging check and creates a GitHub Release with generated notes.

## GitHub settings that can only be changed in the web UI

- Settings > Branches > add a rule for `main`: require a pull request before merging, require status checks to pass (Unit and API tests, Docker build and smoke test, Monitoring stack check), and require approval.
- Settings > Actions > General > Workflow permissions: allow read and write if publishing to the registry is blocked.
- Issues and Projects: enable a Projects board to plan work.
