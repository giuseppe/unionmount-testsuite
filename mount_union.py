from tool_box import *

def mount_union(ctx):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    testdir = cfg.testdir()
    if cfg.testing_none() and not cfg.testing_snapshot():
        lower_mntroot = cfg.lower_mntroot()
        system("mount -o remount,rw " + lower_mntroot)
        system("mount -o bind " + lower_mntroot + " " + union_mntroot)
        ctx.note_upper_fs(lower_mntroot, testdir)

    else:
        lower_mntroot = cfg.lower_mntroot()
        upper_mntroot = cfg.upper_mntroot()
        snapshot_mntroot = cfg.snapshot_mntroot()
        if cfg.is_samefs():
            base_mntroot = cfg.base_mntroot()
            system("mount -o remount,rw " + base_mntroot)
            try:
                os.mkdir(base_mntroot + upper_mntroot)
            except OSError:
                pass
            system("mount -o bind " + base_mntroot + upper_mntroot + " " + upper_mntroot)
        else:
            system("mount " + upper_mntroot + " 2>/dev/null"
                    " || mount -t tmpfs upper_layer " + upper_mntroot)
        layer_mntroot = upper_mntroot + "/" + ctx.curr_layer()
        upperdir = layer_mntroot + "/u"
        workdir = layer_mntroot + "/w"
        try:
            os.mkdir(layer_mntroot)
        except OSError:
            system("rm -rf " + upper_mntroot + "/*")
            os.mkdir(layer_mntroot)
        # Create unique fs for upper/0 if maxfs > 0
        if cfg.maxfs() > 0:
            system("mount -t tmpfs " + ctx.curr_layer() + "_layer " + layer_mntroot)
        os.mkdir(upperdir)
        os.mkdir(workdir)

        if cfg.testing_snapshot():
            system("mount -o remount,rw " + lower_mntroot)
            mnt = snapshot_mntroot
        else:
            mnt = union_mntroot
        mntopt = " -orw" + cfg.mntopts()
        system("mount -t overlay overlay " + mnt + mntopt +
               ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir)
        if cfg.testing_snapshot():
            system("mount -t snapshot snapshot " + union_mntroot +
                    " -oupperdir=" + lower_mntroot + ",snapshot=" + snapshot_mntroot)
            ctx.note_upper_fs(lower_mntroot, testdir)
        else:
            ctx.note_upper_fs(upper_mntroot, testdir)
        ctx.note_lower_layers(lower_mntroot)
        ctx.note_upper_layer(upperdir)
