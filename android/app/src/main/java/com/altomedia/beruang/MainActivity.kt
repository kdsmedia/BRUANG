package com.altomedia.beruang

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.webkit.WebSettingsCompat
import androidx.webkit.WebViewFeature
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.postgrest.Postgrest
import io.github.jan.supabase.auth.Auth

/**
 * Supabase client shared across the app.
 * Connected to project jzyfxdysukzvnfllcbvq with the publishable anon key.
 */
val supabase = createSupabaseClient(
    supabaseUrl = "https://jzyfxdysukzvnfllcbvq.supabase.co",
    supabaseKey = "sb_publishable_DgATc8UqYXx8qneQC8fi3A_dF_ZT6Lx"
) {
    install(Postgrest)
    install(Auth)
}

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private var filePathCallback: ValueCallback<Array<Uri>>? = null

    private val cameraPermissionLauncher: ActivityResultLauncher<String> =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                notifyCameraPermissionGranted()
            }
        }

    private val fileChooserLauncher: ActivityResultLauncher<Array<String>> =
        registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            val result = if (uri != null) arrayOf(uri) else null
            filePathCallback?.onReceiveValue(result)
            filePathCallback = null
        }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Edge-to-edge so the WebView renders behind system bars; the web app
        // handles top/bottom insets via CSS env(safe-area-inset-*). Required for
        // correct viewport on Android 15+ (targetSdk >= 35 enforces edge-to-edge).
        enableEdgeToEdge()

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            settings.allowFileAccess = false
            settings.allowContentAccess = true
            settings.cacheMode = android.webkit.WebSettings.LOAD_DEFAULT
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            settings.mixedContentMode =
                android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW

            webViewClient = WebViewClient()
            webChromeClient = object : WebChromeClient() {
                override fun onPermissionRequest(request: PermissionRequest) {
                    val resources = request.resources
                    val granted = mutableListOf<String>()
                    for (res in resources) {
                        if (res == PermissionRequest.RESOURCE_VIDEO_CAPTURE) {
                            val perm = Manifest.permission.CAMERA
                            if (ContextCompat.checkSelfPermission(
                                    this@MainActivity, perm
                                ) == PackageManager.PERMISSION_GRANTED
                            ) {
                                granted.add(res)
                            } else {
                                cameraPermissionLauncher.launch(perm)
                                request.deny()
                                return
                            }
                        }
                    }
                    if (granted.isNotEmpty()) {
                        request.grant(granted.toTypedArray())
                    } else {
                        request.deny()
                    }
                }

                override fun onShowFileChooser(
                    webView: WebView?,
                    callback: ValueCallback<Array<Uri>>?,
                    fileChooserParams: FileChooserParams?
                ): Boolean {
                    filePathCallback?.onReceiveValue(null)
                    filePathCallback = callback
                    val accept = fileChooserParams?.acceptTypes
                        ?.filter { it.isNotEmpty() }
                        ?.toTypedArray()
                        ?: arrayOf("image/*")
                    try {
                        fileChooserLauncher.launch(accept)
                    } catch (e: Exception) {
                        filePathCallback?.onReceiveValue(null)
                        filePathCallback = null
                        return false
                    }
                    return true
                }
            }

            // Expose Supabase config to the web app so it can confirm native integration.
            addJavascriptInterface(
                object {
                    @android.webkit.JavascriptInterface
                    fun supabaseUrl(): String = "https://jzyfxdysukzvnfllcbvq.supabase.co"

                    @android.webkit.JavascriptInterface
                    fun supabaseKey(): String =
                        "sb_publishable_DgATc8UqYXx8qneQC8fi3A_dF_ZT6Lx"

                    @android.webkit.JavascriptInterface
                    fun appVersion(): String =
                        packageManager.getPackageInfo(packageName, 0).versionName ?: "1.0.0"

                    @android.webkit.JavascriptInterface
                    fun isNative(): Boolean = true
                },
                "AndroidBridge"
            )
        }

        setContentView(webView)

        if (WebViewFeature.isFeatureSupported(WebViewFeature.SAFE_BROWSING_ENABLE)) {
            try {
                WebSettingsCompat.setSafeBrowsingEnabled(webView.settings, true)
            } catch (_: Exception) { /* best-effort */ }
        }

        webView.loadUrl("file:///android_asset/web/index.html")
    }

    private fun notifyCameraPermissionGranted() {
        webView.evaluateJavascript(
            "if(window.navigator && navigator.mediaDevices){navigator.mediaDevices.getUserMedia({video:true}).catch(function(){})}",
            null
        )
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.apply {
            stopLoading()
            removeAllViews()
            destroy()
        }
        super.onDestroy()
    }
}
