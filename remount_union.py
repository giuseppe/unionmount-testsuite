from tool_box import *

def remount_union(ctx, rotate_upper=False):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    lower_mntroot = cfg.lower_mntroot()
    snapshot_mntroot = cfg.snapshot_mntroot()

    if cfg.testing_snapshot():
        system("umount " + snapshot_mntroot)
        check_not_tainted()
        mnt = snapshot_mntroot
    else:
        mnt = union_mntroot

    if cfg.testing_overlayfs() or cfg.testing_snapshot():
        system("umount " + cfg.union_mntroot())
        system("echo 3 > /proc/sys/vm/drop_caches")
        check_not_tainted()

        upper_mntroot = cfg.upper_mntroot()
        if rotate_upper and ctx.have_more_layers():
            lowerlayers = ctx.upper_layer() + ":" + ctx.lower_layers()
            layer_mntroot = upper_mntroot + "/" + ctx.next_layer()
            upperdir = layer_mntroot + "/u"
            workdir = layer_mntroot + "/w"
            os.mkdir(layer_mntroot)
            # Create unique fs for upper/N if N < maxfs
            if ctx.have_more_fs():
                system("mount -t tmpfs " + ctx.curr_layer() + "_layer " + layer_mntroot)
            os.mkdir(upperdir)
            os.mkdir(workdir)
        else:
            lowerlayers = ctx.lower_layers()
            layer_mntroot = upper_mntroot + "/" + ctx.curr_layer()
            upperdir = layer_mntroot + "/u"
            workdir = layer_mntroot + "/w"

        mntopt = " -orw" + cfg.mntopts()
        cmd = "mount -t overlay overlay " + mnt + mntopt + ",lowerdir=" + lowerlayers + ",upperdir=" + upperdir + ",workdir=" + workdir
        system(cmd)
        if cfg.is_verbose():
            write_kmsg(cmd);
        if cfg.testing_snapshot():
            system("mount -t snapshot snapshot " + union_mntroot +
                    " -oupperdir=" + lower_mntroot + ",snapshot=" + snapshot_mntroot)
        ctx.note_upper_fs(upper_mntroot, cfg.testdir())
        ctx.note_lower_layers(lowerlayers)
        ctx.note_upper_layer(upperdir)
