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
 * TSEvalModuleHelper.java
 * Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.classifiers.timeseries.eval;

import java.lang.reflect.Method;
import java.util.List;
import weka.core.WekaPackageClassLoaderManager;

public class TSEvalModuleHelper {

  /**
   * Calls the TSEvalModule.getModuleList.
   *
   * @return the list of TSEvalModule objects
   */
  public static List getModuleList() {
    try {
      Class cls = WekaPackageClassLoaderManager.forName("weka.classifiers.timeseries.eval.TSEvalModule");
      Method method = cls.getMethod("getModuleList");
      return (List) method.invoke(null);
    }
    catch (Exception e) {
      System.err.println("Failed to query TSEvalModule object:");
      e.printStackTrace();
      return null;
    }
  }

  /**
   * Calls the TSEvalModule.getModule.
   *
   * @param name the name of the module
   * @return the TSEvalModule instance
   */
  public static Object getModule(String name) {
    try {
      Class cls = WekaPackageClassLoaderManager.forName("weka.classifiers.timeseries.eval.TSEvalModule");
      Method method = cls.getMethod("getModule", String.class);
      return method.invoke(null, name);
    }
    catch (Exception e) {
      System.err.println("Failed to get TSEvalModule object with name: " + name);
      e.printStackTrace();
      return null;
    }
  }
}
