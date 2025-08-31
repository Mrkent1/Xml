using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

namespace AntiFakeXML.Core;

public static class FileTimeUtil
{
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern SafeFileHandle CreateFile(string lpFileName, uint dwDesiredAccess, uint dwShareMode,
        IntPtr lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetFileTime(SafeFileHandle hFile, ref long lpCreationTime, ref long lpLastAccessTime, ref long lpLastWriteTime);

    private const uint GENERIC_WRITE = 0x40000000;
    private const uint FILE_SHARE_READ = 0x00000001;
    private const uint FILE_SHARE_WRITE = 0x00000002;
    private const uint OPEN_EXISTING = 3;
    private const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;

    public static void OverwriteBytesKeepTimes(string path, byte[] newBytes)
    {
        var fi = new FileInfo(path);
        var c = fi.CreationTimeUtc.ToFileTimeUtc();
        var a = fi.LastAccessTimeUtc.ToFileTimeUtc();
        var w = fi.LastWriteTimeUtc.ToFileTimeUtc();

        File.WriteAllBytes(path, newBytes);
        using var handle = CreateFile(path, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, IntPtr.Zero, OPEN_EXISTING, 0, IntPtr.Zero);
        if (!handle.IsInvalid)
        {
            SetFileTime(handle, ref c, ref a, ref w);
        }
    }
}