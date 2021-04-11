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
 * KernelHelper.java
 * Copyright (C) 2014 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.classifiers;

import java.beans.BeanInfo;
import java.beans.Introspector;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Method;

import weka.classifiers.functions.SMO;
import weka.classifiers.functions.SMOreg;
import weka.classifiers.functions.supportVector.Kernel;
import weka.classifiers.functions.supportVector.RBFKernel;
import weka.classifiers.trees.J48;
import weka.core.Utils;

/**
 * Helper class for kernels.
 *
 * @author FracPete (pythonwekawrapper at gmail dot com)
 */
public class KernelHelper {

  /**
   * Returns the (first) kernel property of the object. 
   *
   * @param obj the object to get the kernel property from
   * @return the kernel property, null if object doesn't have one
   */
  public static PropertyDescriptor getKernelProperty(Object obj) {
    PropertyDescriptor		result;
    BeanInfo			info;
    PropertyDescriptor[]	props;
    Class			cls;
    
    result = null;
    
    try {
      info  = Introspector.getBeanInfo(obj.getClass());
      props = info.getPropertyDescriptors();
      for (PropertyDescriptor prop: props) {
	if ((prop.getWriteMethod() == null) || (prop.getReadMethod() == null))
	  continue;
	cls = prop.getReadMethod().getReturnType();
	if (cls == Kernel.class) {
	  result = prop;
	  break;
	}
      }
    }
    catch (Exception e) {
      result = null;
      System.err.println("Failed to process property descriptors:");
      e.printStackTrace();
    }
    
    return result;
  }

  /**
   * Checks whether the provided object has a Kernel bean property.
   *
   * @param obj the object to check
   * @return true if the object has a kernel property
   */
  public static boolean hasKernelProperty(Object obj) {
    return (getKernelProperty(obj) != null);
  }

  /**
   * Sets the kernel.
   *
   * @param obj the object to set the kernel for
   * @param kernel the kernel to set
   * @return true if the kernel was set successfully
   */
  public static boolean setKernel(Object obj, Kernel kernel) {
    boolean		result;
    PropertyDescriptor	prop;
    Method		write;
    
    result = false;
    
    prop = getKernelProperty(obj);
    if (prop != null) {
      try {
	write = prop.getWriteMethod();
	write.invoke(obj, new Object[]{kernel});
	result = true;
      }
      catch (Exception e) {
	System.err.println("Failed to set kernel:");
	e.printStackTrace();
      }
    }
    
    return result;
  }
  
  /**
   * Gets the kernel.
   * 
   * @param obj the object to get the kernel from
   * @return the kernel, null if failed to obtain
   */
  public static Kernel getKernel(Object obj) {
    Kernel		result;
    PropertyDescriptor	prop;
    Method		read;
    
    result = null;
    
    prop = getKernelProperty(obj);
    if (prop != null) {
      try {
	read   = prop.getReadMethod();
	result = (Kernel) read.invoke(obj, new Object[0]);
      }
      catch (Exception e) {
	System.err.println("Failed to get kernel:");
	e.printStackTrace();
      }
    }
    
    return result;
  }
  
  /**
   * For testing only.
   * 
   * @param args	commandline args - ignored
   */
  public static void main(String[] args) throws Exception {
    Kernel kernel = new RBFKernel();
    Classifier cls; 
    
    cls = new SMO();    
    System.out.println("\n--> " + cls.getClass().getName());
    System.out.println("has kernel? " + hasKernelProperty(cls));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
    System.out.println("set kernel? " + setKernel(cls, kernel));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
    
    cls = new SMOreg();    
    System.out.println("\n--> " + cls.getClass().getName());
    System.out.println("has kernel? " + hasKernelProperty(cls));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
    System.out.println("set kernel? " + setKernel(cls, kernel));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
    
    cls = new J48();    
    System.out.println("\n--> " + cls.getClass().getName());
    System.out.println("has kernel? " + hasKernelProperty(cls));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
    System.out.println("set kernel? " + setKernel(cls, kernel));
    System.out.println("kernel: " + Utils.toCommandLine(getKernel(cls)));
  }
}
