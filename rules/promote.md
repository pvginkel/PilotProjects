# A promotion

What a promotion to production needs, the same in every project: the job and its parameter, the
wait on the build, the read of production through `cexec iac`, and the check for what else is
running. The worker runs outside the store, so a promotion's brief carries the text below,
copied verbatim, as it carries the grants (`rules/work-items.md`); the brief names the rest, the
application, the commit and what the close-out owes after it.

Pilot starts a promotion's work item where the handbook's rules on other work running let it,
and a close-out's promotion besides only once the run's continuation has ended
(`rules/routing.md`'s Deferral): what else of the project runs is Pilot's check, made before the
start, never the worker's.

## In a promotion's brief

```text
A promotion to production, the same in every project:

- The job: the application's promotion job, `<App>/Promote-PRD`, in its Jenkins folder beside its
  build job, `<App>/Build-Main`. It runs `Jenkinsfile.promote` in the application's deploy
  repository, whose header names the job on its `Job:` line and says what each parameter takes:
  that header is the one read the job needs. PilotApp's is `PilotApp/Promote-PRD`, in PilotDeploy,
  with one parameter, `commit`: the commit on PilotDeploy's `main` to promote, its tip when empty.
- The build first: what is promoted is a build the dev stage already runs. Wait on the build of
  the application's commit the brief names, the pipelines it triggers and the dev stage's roll:
  `timeout 1800 track_build.py <App>/Build-Main --hash <the application's commit> --diagnose`
  (in `~/.local/bin`), whose summary and exit status say how each went. A build that failed is
  reported, never promoted.
- What else is running: Pilot started this work where the project's rules on other work running
  let it, and that check is Pilot's, never yours: a session you see running holds nothing. The
  job's own builds are yours to read: `curl -fsS -u "$JENKINS_USER:$JENKINS_TOKEN"
  "$JENKINS_URL/job/<App>/job/Promote-PRD/api/json?tree=nextBuildNumber,lastBuild%5Bnumber,building%5D"`.
  A last build still building is another promotion: follow it to its end with
  `track_build.py <App>/Promote-PRD --buildnr <its number>` before you start yours.
- The start and its wait: the job's `nextBuildNumber`, read as above, is the build your start
  makes. Start it through Jenkins's API, a `--data-urlencode` for each parameter its header names;
  PilotApp's: `curl -fsS -X POST -u "$JENKINS_USER:$JENKINS_TOKEN"
  "$JENKINS_URL/job/<App>/job/Promote-PRD/buildWithParameters" --data-urlencode "commit=<commit>"`.
  Then wait on it through production's roll:
  `timeout 1800 track_build.py <App>/Promote-PRD --buildnr <n> --diagnose`.
- Production, read: kubectl runs in the `iac` tool container, `cexec iac kubectl …`, on the
  default kubeconfig, whose context `prd` is production's; a read is all a promotion needs of it.
  The stage's pods and the image each runs show what production now runs; PilotApp's:
  `cexec iac kubectl -n pilot-prd get pods -l app.kubernetes.io/name=pilot -o jsonpath='{..image}'`,
  which names the build promoted as `prd-<n>`.
- Your turn's last line names the promotion's build, the commit it promoted and the image
  production runs.
```
