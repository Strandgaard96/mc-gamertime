import { z } from "zod";

const endOfTomorrow = new Date();
endOfTomorrow.setDate(endOfTomorrow.getDate() + 1);
endOfTomorrow.setHours(23, 59, 59, 999);

export const ResultFormSchema = z.object({
  gameId: z.string().min(1, "Please select a game"),

  date: z.coerce
    .date({
      message: "Must be a valid date", // <-- Just use 'message'
    })
    .max(endOfTomorrow, "Date cannot be in the future"),

  players: z.array(z.string()).min(1, "Please select at least 1 player"),
  winnerId: z.string().min(1, "Please select a winner"),
});
