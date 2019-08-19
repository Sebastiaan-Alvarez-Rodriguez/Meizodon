AmandroidMain.main(args)

/*******************************************************************************
 * Copyright (c) 2013 - 2016 Fengguo Wei and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 ******************************************************************************/
import java.io.File
import java.net.URL
import java.net.URLClassLoader

object AmandroidMain extends App {
  if(args.size < 2) {
    println("""
Usage: amandroid your.main.class.name arg1 arg2 arg3 ...
""")
    System.exit(-1)
  }
  final val AMANDROID_DIST_KEY = "AMANDROID_DIST"
  val amandroidDir = new File(args(0))
  var _addedClasspathURLs = Set[String]()
  updateClasspath(amandroidDir)
  
  val cliargs = args.slice(1, args.length)
  val clazz = cliargs.head + "$"
  val myargs = cliargs.tail
  val c = Class.forName(clazz)
  val cons = c.getDeclaredConstructors()
  cons(0).setAccessible(true)
  val m = c.getMethod("main", classOf[Array[String]])
  m.setAccessible(true)
  m.invoke(cons(0).newInstance(), myargs)
  
  val isDevelopment = {
    val d = System.getenv(AMANDROID_DIST_KEY)
    if (d == null || d.trim != "true") true else false
  }
  
  def updateClasspath(baseDir: File) {
    if (isDevelopment)
      return

    val libDir = new File(baseDir, "lib")
    if (libDir.exists)
      for (f <- libDir.listFiles) {
        if (f.getName.endsWith(".jar"))
          addClasspathURL(f.toURI.toURL)
      }
  }
  
  def addClasspathURL(url: URL) {
    val urlText = url.toString
    if (!_addedClasspathURLs.contains(urlText)) {
      _addedClasspathURLs = _addedClasspathURLs + urlText
      val sysLoader = getClass.getClassLoader.asInstanceOf[URLClassLoader]
      val sysClass = classOf[URLClassLoader]
      val m = sysClass.getDeclaredMethod("addURL", classOf[URL])
      m.setAccessible(true)
      m.invoke(sysLoader, url)
    }
  }
  
}