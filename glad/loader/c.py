
LOAD_OPENGL_DLL = '''
%(pre)s void* %(proc)s_%(api)s(const char *namez);

#if defined(_WIN32)
static const char *NAMES_gl[] = {"opengl32.dll"};
static const char *NAMES_gles2[] = {"libGLESv3.dll", "libGLESv2.dll"};
static const char *GET_PROC_NAMES_gl[] = {"wglGetProcAddress"};
static const char *GET_PROC_NAMES_gles2[] = {"eglGetProcAddress"};
#elif defined(__APPLE__)
static const char *NAMES_gl[] = {
    "../Frameworks/OpenGL.framework/OpenGL",
    "/Library/Frameworks/OpenGL.framework/OpenGL",
    "/System/Library/Frameworks/OpenGL.framework/OpenGL",
    "/System/Library/Frameworks/OpenGL.framework/Versions/Current/OpenGL"
};
#elif defined(__ANDROID__)
static const char *NAMES_gl[] = {"libEGL.so"};
static const char *NAMES_gles2[] = {"libEGL.so"};
static const char *GET_PROC_NAMES_gl[] = {"eglGetProcAddress"};
static const char *GET_PROC_NAMES_gles2[] = {"eglGetProcAddress"};
#else
static const char *NAMES_gl[] = {"libGL.so.1", "libGL.so"};
static const char *NAMES_gles2[] = {"libGLESv3.so", "libGLESv2.so"};
static const char *GET_PROC_NAMES_gl[] = {"glXGetProcAddress"};
static const char *GET_PROC_NAMES_gles2[] = {"glXGetProcAddress"};
#endif


#ifdef _WIN32
#include <windows.h>
static HMODULE lib_%(api)s;
typedef void* (APIENTRYP PFNWGLGETPROCADDRESSPROC_PRIVATE)(const char*);
static PFNWGLGETPROCADDRESSPROC_PRIVATE gladGetProcAddressPtr;
#else
#include <dlfcn.h>
static void* lib_%(api)s;
#ifndef __APPLE__
typedef void* (APIENTRYP PFNGLXGETPROCADDRESSPROC_PRIVATE)(const char*);
static PFNGLXGETPROCADDRESSPROC_PRIVATE gladGetProcAddressPtr;
#endif
#endif

%(pre)s
int %(init)s_%(api)s(void) {
    unsigned int index = 0;
    for(index = 0; index < (sizeof(NAMES_%(api)s) / sizeof(NAMES_%(api)s[0])); index++) {

#ifdef _WIN32
        lib_%(api)s = LoadLibraryA(NAMES_%(api)s[index]);
#else
        lib_%(api)s = dlopen(NAMES_%(api)s[index], RTLD_NOW | RTLD_GLOBAL);
#endif

        if(lib_%(api)s != NULL) {
#if defined(__APPLE__)
            return 1;
#elif defined(_WIN32)
            gladGetProcAddressPtr = (PFNWGLGETPROCADDRESSPROC_PRIVATE)GetProcAddress(
                lib_%(api)s, GET_PROC_NAMES_%(api)s[index]);
            return gladGetProcAddressPtr != NULL;
#else
            gladGetProcAddressPtr = (PFNGLXGETPROCADDRESSPROC_PRIVATE)dlsym(lib_%(api)s,
                GET_PROC_NAMES_%(api)s[index]);
            return gladGetProcAddressPtr != NULL;
#endif
        }
    }

    return 0;
}

%(pre)s
void %(terminate)s_%(api)s() {
    if(lib_%(api)s != NULL) {
#ifdef _WIN32
        FreeLibrary(lib_%(api)s);
#else
        dlclose(lib_%(api)s);
#endif
        lib_%(api)s = NULL;
    }
}

%(pre)s
void* %(proc)s_%(api)s(const char *namez) {
    void* result = NULL;
    if(lib_%(api)s == NULL) return NULL;

#ifndef __APPLE__
    if(gladGetProcAddressPtr != NULL) {
        result = gladGetProcAddressPtr(namez);
    }
#endif
    if(result == NULL) {
#ifdef _WIN32
        result = (void*)GetProcAddress(lib_%(api)s, namez);
#else
        result = dlsym(lib_%(api)s, namez);
#endif
    }

    return result;
}
'''

LOAD_OPENGL_DLL_H = '''
'''

LOAD_OPENGL_GLAPI_H = '''
#ifndef GLAPI
# if defined(GLAD_GLAPI_EXPORT)
#  if defined(WIN32) || defined(__CYGWIN__)
#   if defined(GLAD_GLAPI_EXPORT_BUILD)
#    if defined(__GNUC__)
#     define GLAPI __attribute__ ((dllexport)) extern
#    else
#     define GLAPI __declspec(dllexport) extern
#    endif
#   else
#    if defined(__GNUC__)
#     define GLAPI __attribute__ ((dllimport)) extern
#    else
#     define GLAPI __declspec(dllimport) extern
#    endif
#   endif
#  elif defined(__GNUC__) && defined(GLAD_GLAPI_EXPORT_BUILD)
#   define GLAPI __attribute__ ((visibility ("default"))) extern
#  else
#   define GLAPI extern
#  endif
# else
#  define GLAPI extern
# endif
#endif
'''

