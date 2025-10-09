#include "starboard/android/shared/accessibility_extension.h"

#include "starboard/extension/accessibility.h"

namespace starboard {

// ATV no longer supports GetTextToSpeechSettings in Chrobalt,
// so this function is stubbed out.
bool GetTextToSpeechSettings(SbAccessibilityTextToSpeechSettings* out_setting) {
  return false;
}

}  // namespace starboard
