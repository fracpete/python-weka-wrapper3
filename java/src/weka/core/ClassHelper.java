/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * ClassHelper.java
 * Copyright (C) 2018-2021 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.core;

import weka.Run;
import java.beans.BeanInfo;
import java.beans.Introspector;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Array;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

/**
 * Helper class for classes.
 *
 * @author FracPete (pythonwekawrapper at gmail dot com)
 */
public class ClassHelper {

  /**
   * Returns the class associated with the classname.
   *
   * @param classname the class to load
   * @return the class
   * @throws Exception if instantiation fails
   */
  public static Class getClass(String classname) throws Exception {
    return WekaPackageClassLoaderManager.forName(classname);
  }

  /**
   * Returns the class given its class name.
   *
   * @param classType the class that an instantiated object should be
   *          assignable to -- an exception is thrown if this is not the case
   * @param className the fully qualified class name
   * @return the class.
   * @throws Exception if the class name is invalid, or if the class is not
   *              assignable to the desired class type, or the options supplied
   *              are not acceptable to the object
   */
  public static Class forName(Class<?> classType, String className) throws Exception {
    List<String> matches = Run.findSchemeMatch(classType, className, false, true);
    if (matches.size() == 0)
      return getClass(className);

    if (matches.size() > 1) {
      StringBuffer sb = new StringBuffer("More than one possibility matched '" + className + "':\n");
      for (String s : matches)
        sb.append("  " + s + '\n');
      throw new Exception(sb.toString());
    }

    className = matches.get(0);

    Class<?> c = null;
    try {
      return getClass(className);
    }
    catch (Exception ex) {
      throw new Exception("Can't find a permissible class called: " + className);
    }
  }

  /**
   * Creates a new instance of a class.
   *
   * @param classname the name of the class to instantiate
   * @param signature the classes of the constructor
   * @param values the values for the constructor
   * @return the instance, null if failed to instantiate
   */
  public static Object newInstance(String classname, Class[] signature, Object[] values) {
    try {
      Class cls = getClass(classname);
      Constructor constr = cls.getConstructor(signature);
      return constr.newInstance(values);
    }
    catch (Exception e) {
      System.err.println("Failed to initialize " + classname + ":");
      e.printStackTrace();
      return null;
    }
  }

  /**
   * Calls a static method.
   *
   * @param classname the name of the class
   * @param methodname the name of the method
   * @param signature the classes of the method
   * @param values the values for the method
   * @return the return value, null if failed to invoke
   */
  public static Object invokeStaticMethod(String classname, String methodname, Class[] signature, Object[] values) {
    try {
      Class cls = getClass(classname);
      Method method = cls.getMethod(methodname, signature);
      return method.invoke(null, values);
    }
    catch (Exception e) {
      System.err.println("Failed to get invoke static method " + methodname + " of class " + classname + "!");
      e.printStackTrace();
      return null;
    }
  }

  /**
   * Returns the static field from the specified class.
   *
   * @param classname	the class to load
   * @param fieldname	the static field to return from that class
   * @return		the static field
   * @throws Exception	if loading of class fails or static field not present
   */
  public static Object getStaticField(String classname, String fieldname) throws Exception {
    Class 	cls;
    Field 	field;

    cls = getClass(classname);
    field = cls.getField(fieldname);
    if (field != null)
      return field.get(cls);
    throw new Exception("Failed to obtain static field '" + fieldname + "' from class '" + classname + "'!");
  }

  /**
   * Returns the names of the Bean properties of the object.
   * Eg used by GridSearch or MultiSearch.
   *
   * @param obj 	the object to get the property names from
   * @return 		the property names
   * @throws Exception	if failed to retrieve properties
   */
  public static String[] listPropertyNames(Object obj) throws Exception {
    return listPropertyNames(obj.getClass());
  }

  /**
   * Returns the names of the Bean properties of the class.
   * Eg used by GridSearch or MultiSearch.
   *
   * @param cls 	the class to get the property names from
   * @return 		the property names
   * @throws Exception	if failed to retrieve properties
   */
  public static String[] listPropertyNames(Class cls) throws Exception {
    List<String>			result;
    BeanInfo 				bi;
    PropertyDescriptor[] 	properties;

    result     = new ArrayList<String>();
    bi         = Introspector.getBeanInfo(cls);
    properties = bi.getPropertyDescriptors();

    for (PropertyDescriptor desc: properties) {
      if ((desc == null) || (desc.getReadMethod() == null) || (desc.getWriteMethod() == null))
        continue;
      result.add(desc.getName());
    }

    return result.toArray(new String[0]);
  }

  /**
   * Returns instance of enum.
   *
   * @param classname the name of the enum class
   * @param enm the name of the enum item to return
   * @return the return value, null if failed to invoke
   * @throws Exception if instantation fails
   */
  public static Object getEnum(String classname, String enm) throws Exception {
    Class cls = getClass(classname);
    return invokeStaticMethod("java.lang.Enum", "valueOf", new Class[]{Class.class, String.class}, new Object[]{cls, enm});
  }
}
