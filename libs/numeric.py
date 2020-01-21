class Numeric:
  def duration():
    secs  = int(self)
    mins  = secs / 60
    hours = mins / 60
    days  = hours / 24

    if days > 0:
      return "{}d {}h {}m {}s".format(days, hours % 24, mins % 60, secs % 60)
    elsif hours > 0:
      return "{}h {}m {}s".format(hours, mins % 60, secs % 60)
    elsif mins > 0:
      return "{}m {}s".format(mins, secs % 60)
    elsif secs >= 0:
      return "{}s".format(secs)