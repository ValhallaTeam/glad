from glad.loader import BaseLoader
from glad.loader.c import LOAD_OPENGL_DLL, LOAD_OPENGL_DLL_H, LOAD_OPENGL_GLAPI_H

_OPENGL_LOADER = \
    LOAD_OPENGL_DLL % {'pre':'static', 'init':'open',
                       'proc':'get_proc', 'terminate':'close', 'api':'gl'} + '''
int gladLoadGL(void) {
    if(open_gl()) {
        gladLoadGLLoader(&get_proc_gl);
        close_gl();
        return 1;
    }
    return 0;
}
'''

_OPENGLES2_LOADER = \
    LOAD_OPENGL_DLL % {'pre':'static', 'init':'open',
                       'proc':'get_proc', 'terminate':'close', 'api':'gles2'} + '''
int gladLoadGLES2(void) {
    if(open_gles2()) {
        gladLoadGLES2Loader(&get_proc_gles2);
        close_gles2();
        return 1;
    }
    return 0;
}
'''

_OPENGL_HAS_EXT = '''
struct gladGLversionStruct GLVersion;

#if defined(GL_ES_VERSION_3_0) || defined(GL_VERSION_3_0)
#define _GLAD_IS_SOME_NEW_VERSION 1
#endif

static int has_ext(const char *ext) {
#ifdef _GLAD_IS_SOME_NEW_VERSION
    if(GLVersion.major < 3) {
#endif
        const char *extensions;
        const char *loc;
        const char *terminator;
        extensions = (const char *)glGetString(GL_EXTENSIONS);
        if(extensions == NULL || ext == NULL) {
            return 0;
        }

        while(1) {
            loc = strstr(extensions, ext);
            if(loc == NULL) {
                return 0;
            }

            terminator = loc + strlen(ext);
            if((loc == extensions || *(loc - 1) == ' ') &&
                (*terminator == ' ' || *terminator == '\\0')) {
                return 1;
            }
            extensions = terminator;
        }
#ifdef _GLAD_IS_SOME_NEW_VERSION
    } else {
        int num;
        glGetIntegerv(GL_NUM_EXTENSIONS, &num);

        int index;
        for(index = 0; index < num; index++) {
            const char *e = (const char*)glGetStringi(GL_EXTENSIONS, index);
            if(strcmp(e, ext) == 0) {
                return 1;
            }
        }
    }
#endif

    return 0;
}
'''

_OPENGL_HEADER = '''
#ifndef __glad_h_

#ifdef __gl_h_
#error OpenGL header already included, remove this include, glad already provides it
#endif

#define __glad_h_
#define __gl_h_

#if defined(_WIN32) && !defined(APIENTRY) && !defined(__CYGWIN__) && !defined(__SCITECH_SNAP__)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN 1
#endif
#include <windows.h>
#endif

#ifndef APIENTRY
#define APIENTRY
#endif
#ifndef APIENTRYP
#define APIENTRYP APIENTRY *
#endif

extern struct gladGLversionStruct {
    int major;
    int minor;
} GLVersion;

#ifdef __cplusplus
extern "C" {
#endif

typedef void* (* GLADloadproc)(const char *name);
''' + LOAD_OPENGL_GLAPI_H

_OPENGLES2_HEADER = _OPENGL_HEADER

_OPENGL_HEADER_LOADER = '''
GLAPI int gladLoadGL(void);
''' + LOAD_OPENGL_DLL_H

_OPENGLES2_HEADER_LOADER = '''
GLAPI int gladLoadGLES2(void);
''' + LOAD_OPENGL_DLL_H

_OPENGL_HEADER_END = '''
#ifdef __cplusplus
}
#endif

#endif
'''
_OPENGLES2_HEADER_END = _OPENGL_HEADER_END

_FIND_VERSION = '''
    // Thank you @elmindreda
    // https://github.com/elmindreda/greg/blob/master/templates/greg.c.in#L176
    // https://github.com/glfw/glfw/blob/master/src/context.c#L36
    int i;
    const char* version;
    const char* prefixes[] = {
        "OpenGL ES-CM ",
        "OpenGL ES-CL ",
        "OpenGL ES ",
        NULL
    };

    version = (const char*) glGetString(GL_VERSION);
    if (!version) return;

    for (i = 0;  prefixes[i];  i++) {
        const size_t length = strlen(prefixes[i]);
        if (strncmp(version, prefixes[i], length) == 0) {
            version += length;
            break;
        }
    }

    int major;
    int minor;
    sscanf(version, "%d.%d", &major, &minor);
    GLVersion.major = major; GLVersion.minor = minor;
'''


class OpenGLCLoader(BaseLoader):
    def write(self, fobj, apis):
        if not self.disabled and 'gl' in apis:
            fobj.write(_OPENGL_LOADER)
        if not self.disabled and 'gles2' in apis:
            fobj.write(_OPENGLES2_LOADER)

    def write_begin_load(self, fobj):
        fobj.write('\tGLVersion.major = 0; GLVersion.minor = 0;\n')
        fobj.write('\tglGetString = (PFNGLGETSTRINGPROC)load("glGetString");\n')
        fobj.write('\tif(glGetString == NULL) return;\n')

    def write_find_core(self, fobj):
        fobj.write(_FIND_VERSION);

    def write_has_ext(self, fobj):
        fobj.write(_OPENGL_HAS_EXT)

    def write_header(self, fobj, apis):
        fobj.write(_OPENGL_HEADER)
        if not self.disabled and 'gl' in apis:
            fobj.write(_OPENGL_HEADER_LOADER)
        if not self.disabled and 'gles2' in apis:
            fobj.write(_OPENGLES2_HEADER_LOADER)

    def write_header_end(self, fobj, apis):
        fobj.write(_OPENGL_HEADER_END)
