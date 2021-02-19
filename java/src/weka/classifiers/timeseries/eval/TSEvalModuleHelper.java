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

import java.util.List;
import weka.core.ClassHelper;

public class TSEvalModuleHelper {

  /**
   * Calls the TSEvalModule.getModuleList.
   *
   * @return the list of TSEvalModule objects
   */
  public static List getModuleList() {
    return (List) ClassHelper.invokeStaticMethod("weka.classifiers.timeseries.eval.TSEvalModule", "getModuleList", new Class[0], new Object[0]);
  }

  /**
   * Calls the TSEvalModule.getModule.
   *
   * @param name the name of the module
   * @return the TSEvalModule instance
   */
  public static Object getModule(String name) {
    return ClassHelper.invokeStaticMethod("weka.classifiers.timeseries.eval.TSEvalModule", "getModule", new Class[]{String.class}, new Object[]{name});
  }
}
