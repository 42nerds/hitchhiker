import click
import git
import hitchhiker_module_control.version.semver as semver
import hitchhiker_module_control.version.commit as commit
import hitchhiker_module_control.cli.config as config
import hitchhiker_module_control.enums as enums

@click.command(short_help="Figure out new version and apply it")
@click.option("--show", is_flag=True, default=False, help="print versions and exit")
@click.option("--prerelease", is_flag=True, default=False, help="do prereleases")
@click.pass_context
def version(ctx: click.Context, show, prerelease):
    """Figure out new version and apply it"""
    if show:
        print(f"main version: {ctx.obj.version}")
        for project in ctx.obj.projects:
            print(f"project: {project.name} version: {project.version}")
        return

    print(f"main version: {ctx.obj.version}")
    mainbump = enums.VersionBump.NONE
    changedfiles = []
    for project in ctx.obj.projects:
        print(f"project: {project.name} version: {project.version}")
        bump, commits = commit.find_next_version(ctx.obj, project, prerelease)
        mainbump = bump if bump > mainbump else mainbump
        if bump != enums.VersionBump.NONE:
            project.version.bump_prerelease() if prerelease else project.version.remove_prerelease_and_buildmeta()
            project.version.bump(bump)
            changedfiles += config.set_version(ctx.obj, project)
            print(f"-- new -- project: {project.name} version: {project.version}")
    
    if mainbump != enums.VersionBump.NONE:
        ctx.obj.version.bump_prerelease() if prerelease else ctx.obj.version.remove_prerelease_and_buildmeta()
        ctx.obj.version.bump(mainbump)
        changedfiles += config.set_version(ctx.obj, ctx.obj)
        print(f"main version bump: {ctx.obj.version}")

    if len(changedfiles) > 0:
        ctx.obj.repo.git.add(changedfiles)
        ctx.obj.repo.git.commit(m=f"{str(ctx.obj.version)}\n\nAutogenerated by hitchhiker_module_control")
        newtag = f"v{str(ctx.obj.version)}"
        if newtag not in [tag.name for tag in ctx.obj.repo.tags]:
            ctx.obj.repo.git.tag("-a", newtag, m=newtag)
        else:
            print(f"tag \"{newtag}\" already exists")
